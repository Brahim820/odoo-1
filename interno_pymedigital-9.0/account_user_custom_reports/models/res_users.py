# -*- coding: utf-8 -*-
from openerp import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    check_format_id = fields.Many2one('report.custom.format', string="Check", )
    payment_voucher_format_id = fields.Many2one('report.custom.format', string="Payment voucher", )
    journal_voucher_format_id = fields.Many2one('report.custom.format', string="Journal", )
    income_expenses_voucher_format_id = fields.Many2one('report.custom.format',
        string="Income/Expenses voucher Format")

   # consolidated_payment_format_id = fields.Many2one(
    #    'report.custom.format', string="Consolidated Payment Format", )
