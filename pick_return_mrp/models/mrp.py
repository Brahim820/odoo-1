# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    raw_picking_ids = fields.One2many(
        'stock.picking', inverse_name='mo_id',
        ondelete='restrict', string="Raw material Pickings", )
