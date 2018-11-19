# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _default_comprobante_id(self):
        super(AccountInvoice, self)._default_comprobante_id()
        user = self.env.user
        if user.default_comprobante_id:
            comprobante = user.default_comprobante_id
            return comprobante

    def _default_autorizacion_id(self):
        user = self.env.user
        if user.default_autorizacion_id:
            autorizacion = user.default_autorizacion_id
            return autorizacion

    def _default_secuencial(self):
        user = self.env.user
        secuencial = ''
        if user.default_autorizacion_id:
            autorizacion = user.default_autorizacion_id
            secuencial = str(autorizacion.secuencia_actual + 1)
            if secuencial <= autorizacion.secuencia_final:
                autorizacion.sudo().write({'secuencia_actual': int(secuencial)})
        return secuencial


    comprobante_id = fields.Many2one(default=_default_comprobante_id, )
    autorizacion_id = fields.Many2one(default=_default_autorizacion_id, )
    secuencial = fields.Char(default=_default_secuencial, )
