# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    credit_card_retention = fields.Boolean('¿Retencion de tarjeta de credito?')

    @api.onchange('credit_card_retention')
    def _onchange_credit_card_retention(self):
        for r in self:
            if r.credit_card_retention:
                r.type = 'out_refund'
            if not r.credit_card_retention:
                r.type = 'out_invoice'
