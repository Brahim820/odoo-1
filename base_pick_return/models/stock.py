# -*- coding: utf-8 -*-
from openerp import models, fields


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    pick_return_selectable = fields.Boolean('In Picking and returns', )
