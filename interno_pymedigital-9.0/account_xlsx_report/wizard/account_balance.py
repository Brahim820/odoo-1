# -*- encoding: utf-8 -*-

from openerp import _, api, models
from openerp.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"
    _description = "General Ledger Report"

    def _print_report_xlsx(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        report = self.env['report'].with_context(landscape=True).get_action(
            self, 'account.report_generalledger', data=data)
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
        data['form']['used_context'] = dict(
            used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report_xlsx(data)
