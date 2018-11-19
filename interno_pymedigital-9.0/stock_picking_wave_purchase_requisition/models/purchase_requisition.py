# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )
