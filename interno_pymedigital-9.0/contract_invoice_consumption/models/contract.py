# -*- encoding: utf-8 -*-
from openerp import api, fields, models, _


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    start_qty = fields.Integer(string='start quantity', readonly=True, )
    final_qty = fields.Integer(string='final quantity', readonly=True)
    base_quantity = fields.Integer(string='Base quantity', )













