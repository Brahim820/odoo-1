# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class MaterialPlanWizard(models.TransientModel):
    _inherit = 'mrp.plan.wizard'

    picking_template_ids = fields.Many2many(
        'stock.picking.template',
        'picking_template_mrp_plan_wizard_relation',
        'mrp_plan_wizard_ids',
        'picking_template_ids',
        'Templates', )

    @api.multi
    def complete_products_from_template(self):
        self.planned_items.unlink()

        lines = self.mapped('picking_template_ids').mapped('template_line_ids')
        products = lines.mapped('product_id')
        for product in products:
            uom_obj = self.env['product.uom']
            p_lines = lines.filtered(lambda x: x.product_id == product)
            p_uom = product.uom_id
            qty = sum(p_lines.mapped(lambda line: uom_obj._compute_qty(
                line.product_uom.id,
                line.product_uom_qty,
                p_uom.id
            )))
            print 'Quantity', qty, p_uom
            self.env['mrp.plan.wizard.line'].create({
                'wizard_id': self.id,
                'product_id': product.id,
                'product_qty': qty,
                'product_uom_id': p_uom.id,
            })

    @api.multi
    def action_complete_products_from_template(self):
        self.complete_products_from_template()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.plan.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
