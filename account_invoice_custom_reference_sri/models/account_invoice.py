# -*- coding: utf-8 -*-

from openerp import api, fields, models

class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    @api.multi
    def _get_reference(self):
        res = super(AccountInvoice, self)._get_reference()
        if not self.reference_id:
            return
        res = ' '.join([
                res,
                self.get_sri_secuencial_completo_factura()
            ])
        return res
