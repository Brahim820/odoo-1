# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    def _default_autorizacion_id(self):
        session = self.env['pos.session'].search([('user_id', '=', self.env.user.id), ('state', '=', 'opened')])
        autorizacion = False
        if session:
            autorizacion = session[0].config_id.autorizacion_id
        return autorizacion

    def _default_comprobante_id(self):
        session = self.env['pos.session'].search([('user_id', '=', self.env.user.id), ('state', '=', 'opened')])
        comprobante = False
        if session:
            comprobante = session[0].config_id.autorizacion_id.comprobante_id
        else:
            if self.type in ('in_invoice', 'out_invoice'):
                comprobante = self.env['l10n_ec_sri.comprobante'].search([('code', '=', '01')], limit=1)
            elif self.type in ('in_refund', 'out_refund'):
                comprobante = self.env['l10n_ec_sri.comprobante'].search([('code', '=', '04')], limit=1)
        return comprobante

    def _default_secuencial(self):
        session = self.env['pos.session'].search([('user_id', '=', self.env.user.id), ('state', '=', 'opened')])
        secuencial = ''
        if session:
            autorizacion = session[0].config_id.autorizacion_id
            secuencial = str(autorizacion.secuencia_actual + 1)
            autorizacion.write({'secuencia_actual': int(secuencial)})
        return secuencial

    c_autorizacion_id = fields.Many2one(default=_default_autorizacion_id, )
    secuencial = fields.Char(default=_default_secuencial, )
