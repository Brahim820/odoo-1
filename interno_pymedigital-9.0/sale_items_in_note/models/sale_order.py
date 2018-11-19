# -*- coding: utf-8 -*-
import StringIO
from openerp import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('order_line')
    def _onchange_order_line(self):
        self._set_item_in_note()

    @api.multi
    def _set_item_in_note(self):
        items = ''.join([
            "ITEMS: ",
            str(sum(self.order_line.mapped('product_uom_qty')))
        ])
        comment = self.note or ''

        if comment == '':
            self.note = items
        elif 'ITEMS:' not in comment:
            self.note = comment + "\n" + items
        elif 'ITEMS:' in comment:
            c = u""
            s = StringIO.StringIO(comment)
            for line in s:
                if 'ITEMS:' in line:
                    c += items
                else:
                    c += line
            self.note = c
