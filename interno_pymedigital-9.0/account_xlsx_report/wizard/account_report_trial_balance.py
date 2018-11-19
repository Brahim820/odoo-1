# -*- coding: utf-8 -*-

from openerp import fields, models, api


class AccountBalanceReport(models.TransientModel):
    _inherit = 'account.balance.report'
    _description = 'Trial Balance Report'

    def _print_report_xlsx(self, data):
        data = self.pre_print_report(data)
        report = self.env['report'].get_action(self, 'account.report_trialbalance', data=data)
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
