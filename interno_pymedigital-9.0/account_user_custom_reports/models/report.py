# -*- coding: utf-8 -*-
from openerp import fields, models


class ReportFormatSelector(models.AbstractModel):
    _inherit = 'report.format.selector'

    # Account
    check_format_id = fields.Many2one('report.custom.format', string="Check Format", )
    payment_voucher_format_id = fields.Many2one('report.custom.format', string="Check Format", )
    journal_format_id = fields.Many2one('report.custom.format', string="Journal Format", )
    income_expenses_voucher_format_id = fields.Many2one(
        'report.custom.format',
        string="Income/Expenses voucher Format")

    consolidated_payment_format_id = fields.Many2one(
        'report.custom.format', string="Consolidated Payment Format", )


