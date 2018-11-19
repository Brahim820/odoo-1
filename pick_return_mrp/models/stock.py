# -*- coding: utf-8 -*-
from openerp import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mo_id = fields.Many2one(
        'mrp.production', ondelete='restrict', string='Production', )
    mo_product_id = fields.Many2one(
        'product.product', related='mo_id.product_id', string='Product to Produce', stare=True)
