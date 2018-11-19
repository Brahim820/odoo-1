# -*- coding: utf-8 -*-

from openerp import fields, models
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    product_valuation = fields.Float(
        string='Product valuation',
        digits=dp.get_precision('Product Price'),
    )
    date_valuation = fields.Datetime(string='Date valuation', )

