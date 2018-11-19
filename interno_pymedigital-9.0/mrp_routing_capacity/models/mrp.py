# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    capacity_line_ids = fields.One2many(
        'mrp.capacity.line', inverse_name='routing_id',
        ondelete='restrict', string="Capacity lines", )


class MrpCapacityLine(models.Model):
    _name = 'mrp.capacity.line'

    product_ids = fields.Many2many(
        'product.product', 'product_capacity_line_rel',
        'capacity_line_ids', 'product_ids',
        string='Product variants', )

    product_tmpl_ids = fields.Many2many(
        'product.template', 'product_tmpl_capacity_line_rel',
        'capacity_line_ids', 'product_tmpl_ids',
        string='Product', )

    product_category_ids = fields.Many2many(
        'product.category', 'product_category_capacity_line_rel',
        'capacity_line_ids', 'product_category_ids',
        string='Product categories', )


    routing_id = fields.Many2one(
        'mrp.routing', ondelete='restrict', string="Routing",
        required=True, )

    product_uom_id = fields.Many2one('product.uom', 'Unit of measure', required=True, )
    max_qty = fields.Float('Maximum quantity', required=True, )
    min_qty = fields.Float('Minimum quantity', required=True, )
    opt_qty = fields.Float('Optimum quantity', required=True, )


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def compute_production_qty(self, route=None, uom=None, product=None):
        min_qty = max_qty = opt_qty = self.product_qty
        capacity = self.env['mrp.capacity.line']
        uom = uom or self.product_uom
        bom_uom_categ = uom.category_id
        route = route or self.routing_id
        product = product or self.product_id

        capacity_lines = route.capacity_line_ids
        # Filter only lines with the same uom category.
        capacity_lines = capacity_lines.filtered(lambda x: x.product_uom_id.category_id == bom_uom_categ)

        # Search for lines matching the product.
        for line in capacity_lines:
            print product, self.product_id, line.product_tmpl_ids, line.product_ids, line.product_category_ids

        if product:
            capacity = capacity_lines.filtered(lambda line: product in line.product_ids)

        if not capacity:
            capacity = capacity_lines.filtered(lambda x: product.product_tmpl_id in x.product_tmpl_ids)

        if not capacity:
            capacity = capacity_lines.filtered(lambda x: product.product_tmpl_id.categ_id in x.product_category_ids)

        if capacity:
            min_qty = max(capacity.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.min_qty,
                    uom.id
                )))

            max_qty = min(capacity.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.max_qty,
                    uom.id
                )))

            opt_qty = max(capacity.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.opt_qty,
                    uom.id
                )))

        return min_qty, max_qty, opt_qty
