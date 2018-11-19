# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import _, api, exceptions, fields, models


class StockPickingTemplateLine(models.Model):
    _name = 'stock.picking.template.line'
    _order = 'product_id'

    @api.multi
    @api.onchange('product_id')
    def _onchange_uom_domain(self):
        for r in self:
            uom_category = r.product_id.uom_id.category_id.id
            r.product_uom = r.product_id.uom_id
            return {'domain':{'product_uom': [('category_id', '=', uom_category)]}}

    product_id = fields.Many2one(
        'product.product', ondelete='set null', string="Product",
        required=True, )
    product_uom = fields.Many2one(
        'product.uom', ondelete='set null', string="Product UOM", required=True, )
    product_uom_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), )
    template_id = fields.Many2one('stock.picking.template', string='Template', ondelete='cascade', )


class StockPickingTemplate(models.Model):
    _name = 'stock.picking.template'

    location_src_ids = fields.Many2many(
        'stock.location',
        'location_src_template_relation',
        'template_ids',
        'location_src_ids',
        'Source Locations', )
    name = fields.Char('Name', )
    template_line_ids = fields.One2many(
        'stock.picking.template.line', 'template_id', string='Template lines', )
