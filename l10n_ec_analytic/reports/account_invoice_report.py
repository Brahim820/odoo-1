# -*- coding: utf-8 -*-

from openerp import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    account_analytic_id = fields.Many2one('account.analytic.account', string='Account analityc', readonly=True, )
