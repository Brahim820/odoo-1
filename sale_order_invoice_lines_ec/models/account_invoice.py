# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    secuencial_invoice = fields.Char(related="invoice_id.secuencial", )
