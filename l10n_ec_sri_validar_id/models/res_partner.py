# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api, _
from stdnum.ec import ruc, ci
from stdnum.exceptions import *
from openerp.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat_validation = fields.Boolean(string='Vat validation', default=True, )

    @api.multi
    @api.constrains('vat', 'property_account_position_id')
    def _check_vat(self):
        for r in self:
            if r.vat_validation:
                r.do_check_vat()

    @api.multi
    @api.onchange('vat')
    def _onchange_vat(self):
        for r in self:
            if not r.vat:
                return
            if self.property_account_position_id:
                if r.vat_validation:
                    r.do_check_vat()
            else:
                r._set_fiscal_position()
                if r.vat_validation:
                    r.do_check_vat()

    def _set_fiscal_position(self):
        fiscal = fiscal_obj = self.env['account.fiscal.position']
        vat = self.vat
        # Si tiene 10 dígitos es una cécula
        if len(vat) == 10 and vat.isdigit():
            fiscal = self.env.ref('l10n_ec_sri.fiscal_position_consumidor')
        # Si el tercer dígito es 6 debe ser una institución pública.
        elif len(vat) == 13 and vat.isdigit() and vat[2:3] == '6':
            fiscal = self.env.ref('l10n_ec_sri.fiscal_position_gobierno')
        # Si el tercer dígito es 9 es sociedad o extranjero sin cédula.
        elif len(vat) == 13 and vat.isdigit() and vat[2:3] == '9':
            fiscal = self.env.ref('l10n_ec_sri.fiscal_position_sociedad')
        self.property_account_position_id

    def do_check_vat(self):
        fiscal = self.property_account_position_id
        persona = fiscal.persona_id.code
        identificacion = fiscal.identificacion_id.code

        if identificacion == 'F':
            if not self.vat == '9999999999999':
                raise UserError(
                    _(
                        "El consumidor final debe tener trece números " \
                        "nueve como indentificación: 999999999999"
                    )
                )
        if identificacion == 'R':
            try:
                ruc.validate(self.vat)
            except:
                raise UserError(_("Número de RUC incorrecto."))
        elif identificacion == 'C':
            try:
                ci.validate(self.vat)
            except:
                raise UserError(_("Número de cédula incorrecta"))

