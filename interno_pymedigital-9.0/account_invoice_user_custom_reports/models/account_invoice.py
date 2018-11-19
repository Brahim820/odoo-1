# -*- coding: utf-8 -*-
from openerp import models, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def do_print_retencion(self):
        user = self.env.user
        company = user.company_id
        format_id = user.retencion_format_id or company.default_format_id

        assert format_id, u'Debe definir un formato de impresión'

        page_orientation = format_id.page_orientation or 'portrait'

        return self.env['report'].get_action(self, 'account_invoice_user_custom_reports.retencion_%s_report' % page_orientation)
