# -*- coding: utf-8 -*-

from openerp import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def direct_production(self):
        self.ensure_one()
        return self.action_produce(self.id, self.product_qty, 'consume_produce', False)
