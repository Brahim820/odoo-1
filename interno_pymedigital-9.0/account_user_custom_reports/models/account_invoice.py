# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def do_print_income_expenses_voucher(self):
        user = self.env.user
        company = user.company_id
        format_id = user.income_expenses_voucher_format_id or company.income_expenses_voucher_format_id

        assert format_id, u'Debe definir un formato de impresión'

        if format_id.page_orientation == 'portrait':
            return self.env['report'].get_action(self, 'account_user_custom_reports.report_account_invoice_payments_id')
        elif format_id.page_orientation == 'landscape':
            return self.env['report'].get_action(self, 'account_user_custom_reports.report_account_invoice_payments_id')




