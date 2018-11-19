# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    auto_validate = fields.Boolean(string='Auto validate', )

    @api.multi
    def _create_invoice(self):
        res = super(AccountAnalyticAccount, self)._create_invoice()
        if self.auto_validate:
            res.signal_workflow('invoice_open')
        return res
