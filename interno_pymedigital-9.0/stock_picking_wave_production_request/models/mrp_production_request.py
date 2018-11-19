# -*- coding: utf-8 -*-
from openerp import models, fields, api

class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )
