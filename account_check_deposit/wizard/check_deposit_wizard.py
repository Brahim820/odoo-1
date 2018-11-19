# -*- coding: utf-8 -*-
# Author: Daniel Mendieta
# Copyright 2016 Fábrica de Software Libre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import models, fields, api, _


class CheckDepositReportWizard(models.TransientModel):
    """check deposit report wizard."""

    _name = "check.deposit.report.wizard"
    _inherit = 'bi.abstract.report'
    _description = "Check Deposit Report Wizard"

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    date_type = fields.Selection([
            ('deposit','Deposit date'),
            ('move','Accounting date'),
        ], default="deposit",
        string='Date type',
        )

    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Filter accounts',
    )
    journal_ids = fields.Many2many(
        comodel_name='account.journal',
        domain="[('type','=','bank')]",
        string='Filter journals',
    )
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Filter partners',
    )

    def _get_header(self):
        return [
            _(u'MOVE DATE'),
            _(u'DEPOSIT DATE'),
            _(u'REMAINING DAYS'),
            _(u'PARTNER'),
            _(u'AMOUNT'),
            _(u'PAYMENT'),
            _(u'INVOICES'),
            _(u'REGISTER'),
            _(u'BANK NUMBER'),
        ]

    def _get_aml_vals(self, a):
        try:
            days = (fields.Date.from_string(a.date_deposit) -
                    fields.Date.from_string(fields.Date.today())).days
        except TypeError:
            days = 0
        return [
            a.date or '',
            a.date_deposit or '',
            days,
            a.partner_id.name or '',
            a.debit or 0,
            a.payment_id.name or '',
            ' '.join(a.payment_id.invoice_ids.mapped('number')) or '',
            a.name or '',
            a.bank_match_number or '',
        ]

    @api.multi
    def get_report_data(self):
        header = self._get_header()
        sheets = []

        report_filter = [
            ('reconciled', '=', False),
            ('check_deposit_id', '=', False),
            ('debit', '>', 0)
        ]

        if self.partner_ids:
            report_filter.append(('partner_id', 'in', self.partner_ids.ids))
        if self.account_ids:
            report_filter.append(('account_id', 'in', self.account_ids.ids))
        if self.journal_ids:
            report_filter.append(('journal_id', 'in', self.journal_ids.ids))
        if self.date_type == 'deposit':
            if self.date_from:
                report_filter.append(('date_deposit', '>=', self.date_from))
            if self.date_to:
                report_filter.append(('date_deposit', '<=', self.date_to))
        if self.date_type == 'move':
            if self.date_from:
                report_filter.append(('date', '>=', self.date_from))
            if self.date_to:
                report_filter.append(('date', '<=', self.date_to))

        amls = self.env['account.move.line'].search(report_filter)
        rows = [header]
        for a in amls:
            vals = self._get_aml_vals(a)
            rows.append(vals)

        sheet = {
            'name': 'DEPOSITOS PENDIENTES',
            'rows': rows
        }
        sheets.append(sheet)

        filename = 'check_deposit.xlsx'
        return {
            'wizard': 'check.deposit.report.wizard',
            'filename': filename,
            'sheets': sheets,
        }

