# -*- encoding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import api, fields, models, _
from openerp.exceptions import UserError

class AccountAgedTrialBalance(models.TransientModel):

    _inherit = 'account.aged.trial.balance'
    _description = 'Account Aged Trial balance Report'

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

    def _print_report_xlsx(self, data):
        res = {}
        data = self.pre_print_report(data)
        data['form'].update(self.read(['period_length'])[0])
        period_length = data['form']['period_length']
        if period_length<=0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise UserError(_('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length - 1)
            res[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)
        data['form'].update(res)

        # Segundo intento.
        # ================
        # report_url = "http://localhost:9069/report/html/account.report_agedpartnerbalance?options="
        # import json
        # report_url += json.dumps(data, separators=(',',':'))
        # context = '&context={"lang":"es_EC","tz":"America%2FGuayaquil","uid":1,"params":{"action":225},"active_model":"account.aged.trial.balance","active_id":"","active_ids":"","landscape":true,"search_disable_custom_filters":true}'
        # report_url = report_url + "&" + context
        # print report_url

        report = self.env['report'].with_context(landscape=True).get_action(self, 'account.report_agedpartnerbalance', data=data)
        report['report_type'] = 'qweb-html'
        return report

