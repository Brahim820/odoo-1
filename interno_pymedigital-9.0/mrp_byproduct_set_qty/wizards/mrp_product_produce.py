# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class SubproductToProduceLine(models.TransientModel):
    _name="mrp.subproduct.produce.line"
    _description = "Subproduct to produce lines"

    subproduct_created_id = fields.Many2one('stock.move', string='Create moves', )
    product_uom_qty = fields.Float(
        'Quantity (in default UoM)', digits=dp.get_precision('Product Unit of Measure'), )
    produce_id = fields.Many2one('mrp.product.produce', string="Produce", )
    product_id = fields.Many2one('product.product', related='subproduct_created_id.product_id', string='Product', )


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    subproduct_created_ids = fields.One2many(
        'mrp.subproduct.produce.line', inverse_name='produce_id', string="Subproducts", )

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        production_id = self._context.get('active_id', False)
        production = self.env['mrp.production'].browse(production_id)
        subproductions = production.move_created_ids.filtered(lambda x: x.product_id != production.product_id)
        lines = []
        for subproduction in subproductions:
            lines.append((0, 0, {
                'subproduct_created_id': subproduction.id,
                'produce_id': self.id,
                'product_uom_qty': subproduction.product_uom_qty,
            }))

        self.subproduct_created_ids = lines

    @api.multi
    def do_produce(self):
        production_id = self._context.get('active_id', False)
        production = self.env['mrp.production'].browse(production_id)
        production.produce = self.id

        return super(MrpProductProduce, self).do_produce()
