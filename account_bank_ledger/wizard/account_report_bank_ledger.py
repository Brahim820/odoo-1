# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _name = "account.report.bank.ledger"
    _inherit = "account.common.account.report"
    _description = "Bank Ledger Report"

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal', 'account_report_bank_ledger_journal_rel', 'account_id', 'journal_id',
                                   string='Journals', required=True, default=lambda self: self.env['account.journal'].search([('type','=','bank')]))

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
        res = self.env['report'].with_context(landscape=True).get_action(records, 'account_bank_ledger.report_bankledger', data=data)
        return res

    def _print_report_xlsx(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        report = self.env['report'].with_context(landscape=True).get_action(self, 'account_bank_ledger.report_bankledger',
                                                                            data=data)
        report['report_type'] = 'qweb-html'
        return report

    @api.multi
    def check_report_xlsx(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report_xlsx(data)
