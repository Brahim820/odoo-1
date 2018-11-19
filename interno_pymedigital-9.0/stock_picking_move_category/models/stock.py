# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'product_categ_id'

    product_categ_id = fields.Many2one('product.category', string='Product category', related='product_id.categ_id', store=True, )

