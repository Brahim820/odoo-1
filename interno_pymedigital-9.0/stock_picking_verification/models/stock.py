# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def qty_done_complete(self):
        for spo in self.pack_operation_product_ids:
            spo.qty_done_complete()


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.multi
    def qty_done_complete(self):
        self.ensure_one()
        self.qty_done = self.product_qty
