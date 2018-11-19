# -*- coding: utf-8 -*-
from openerp import models, api

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def do_print_inventory_voucher(self):
        user = self.env.user
        company = user.company_id
        format_id = user.inventory_voucher_format_id or company.default_format_id

        assert format_id, u'Debe definir un formato de impresión'

        page_orientation = format_id.page_orientation or 'portrait'

        return self.env['report'].get_action(self, 'report.inventory_voucher_%s_report' % page_orientation)
