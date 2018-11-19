#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.v7
    def action_consume(self, cr, uid, ids, product_qty, location_id=False, restrict_lot_id=False, restrict_partner_id=False,
                       consumed_for=False, context=None):
        if product_qty > 0:
            return super(StockMove, self).action_consume(cr, uid, ids, product_qty, location_id, restrict_lot_id, restrict_partner_id,
                                                         consumed_for, context)
