# -*- coding: utf-8 -*-
from openerp import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def do_print_journal_voucher(self):
        user = self.env.user
        company = user.company_id
        format_id = user.journal_voucher_format_id or company.journal_voucher_format_id

        assert format_id, u'Debe definir un formato de impresión'

        page_orientation = format_id.page_orientation or 'portrait'

        return self.env['report'].get_action(self, 'report.journal_voucher_%s_report' % page_orientation)
