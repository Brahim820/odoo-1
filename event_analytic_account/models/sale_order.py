# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(compute="_compute_project_id", )

    @api.multi
    @api.depends('event_id', 'event_id.project_id')
    def _compute_project_id(self):
        for order in self:
            analytic = order.event_id.project_id
            order.project_id = analytic

            invoice_ids = order.order_line.mapped('invoice_lines').mapped('invoice_id')
            lines = self.env['account.invoice.line']
            for inv in invoice_ids:
                for line in inv.invoice_line_ids:
                    lines += line
            lines.sudo().write({'account_analytic_id': analytic.id})
