# -*- coding: utf-8 -*-
from openerp import models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def do_print_checks(self):
        user = self.env.user
        company = user.company_id
        format_id = user.check_format_id or company.check_format_id

        assert format_id, u'Debe definir un formato de impresión'

        if format_id.page_orientation == 'portrait':
            return self.env['report'].get_action(self, 'report.check_portrait_report')
        elif format_id.page_orientation == 'landscape':
            return self.env['report'].get_action(self, 'report.check_landscape_report')

    @api.multi
    def do_print_payment_voucher(self):
        user = self.env.user
        company = user.company_id
        format_id = user.payment_voucher_format_id or company.payment_voucher_format_id

        assert format_id, u'Debe definir un formato de impresión'

        if format_id.page_orientation == 'portrait':
            return self.env['report'].get_action(self, 'report.payment_voucher_portrait_report')
        elif format_id and format_id.page_orientation == 'landscape':
            return self.env['report'].get_action(self, 'report.payment_voucher_landscape_report')


    @api.multi
    def do_print_consolidated_payment(self):
        user = self.env.user
        company = user.company_id
        format_id = user.payment_voucher_format_id or company.payment_voucher_format_id

        assert format_id, u'Debe definir un formato de impresión'

        if format_id.page_orientation == 'portrait':
            return self.env['report']. \
                get_action(self, 'account_user_custom_reports.report_account_payments_consolidated_portrait_id')
        elif format_id and format_id.page_orientation == 'landscape':
            return self.env['report'].get_action(self, 'account_user_custom_reports.report_account_payments_consolidated_portrait_id')
