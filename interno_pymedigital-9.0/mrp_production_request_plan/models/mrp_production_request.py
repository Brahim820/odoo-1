# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class MrpProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom = self.product_id.uom_id
        bom = self.env['mrp.bom']._bom_find(
            product_id=self.product_id.id, properties=[])
        self.bom_id = bom
        self.routing_id = self.env['mrp.bom'].browse(bom).routing_id
