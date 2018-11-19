# -*- coding: utf-8 -*-

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def update_price(self):
        if not (self.order_line and self.pricelist_id):
            return
        for li in self.order_line:
            li.product_uom_change()
