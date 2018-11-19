# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    state_invoice = fields.Selection(related="invoice_id.state", )
    date_invoice = fields.Date(related='invoice_id.date_invoice', )
