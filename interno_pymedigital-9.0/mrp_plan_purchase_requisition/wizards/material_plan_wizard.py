# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class MaterialNeedWizardLine(models.TransientModel):
    _inherit = 'mrp.need.wizard.line'

    state = fields.Selection([
        ('pending', 'pending'),
        ('todo', 'To do'),
        ('done', 'Done'),
    ], default='todo', string="State", )


class MaterialPlanWizard(models.TransientModel):
    _inherit = 'mrp.plan.wizard'

    purchase_responsible = fields.Many2one('res.users', string='Responsible', )
    purchase_schedule_date = fields.Date('Schedule date', )
    purchase_picking_type_id = fields.Many2one('stock.picking.type', string='Picking type', )

    @api.multi
    def create_purchase_requisition(self):
        lines = self.needed_items
        requisition_lines = []
        for line in lines:
            if line.state == 'todo':
                requisition_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'schedule_date': self.purchase_schedule_date,
                }))
                line.write({'state':'done', })

        self.env['purchase.requisition'].create({
            'exclusive': 'multiple',
            'schedule_date': self.purchase_schedule_date,
            'picking_type_id': self.purchase_picking_type_id.id,
            'line_ids': requisition_lines,
        })


    @api.multi
    def action_create_purchase_requisition(self):
        self.create_purchase_requisition()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.plan.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }
