# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api

class Wizard(models.TransientModel):
    _name = "mrp_cleanup_for_production.wizard"
    _description = "Cleans database to use on production."

    date_from = fields.Date('Date from', )
    date_to = fields.Date('Date to', )

    limit = fields.Integer('Limit records', )

    cleanup_mrp_production = fields.Boolean(string="Clean up MRP Productions", )

    production_state = fields.Selection([
            ('draft','Draft'),
            ('cancelled', 'Cancelled'),
            ('confirmed', 'Pro-forma'),
            ('ready', 'Ready to produce'),
            ('in_production', 'Production started'),
            ('cancel', 'Done'),
        ], string='Status', copy=False, )

    cleanup_products_to_consume = fields.Boolean(string="Clean up products to consume", )
    cleanup_consumed_products = fields.Boolean(string="Clean up consumed products", )
    cleanup_products_to_produce = fields.Boolean(string="Clean up products to produce", )
    cleanup_produced_products = fields.Boolean(string="Clean up produced products", )
    cleanup_scheduled_products = fields.Boolean(string="Clean up scheduled products", )
    cleanup_work_orders = fields.Boolean(string="Clean up Work orders", )

    cleanup_stock_moves = fields.Boolean(string="Clean up MRP Productions", )

    @api.multi
    def button_cleanup(self):
        for r in self:
            if r.cleanup_mrp_production:
                productions = self.env['mrp.production'].search([])

                if r.production_state:
                    productions = productions.filtered(lambda p: p.state == r.production_state)
                if r.date_from:
                    productions = productions.filtered(lambda p: p.date_planned >= r.date_from)
                if r.date_to:
                    productions = productions.filtered(lambda p: p.date_planned <= r.date_to)
                if r.limit:
                    limit = int(r.limit)
                    productions = productions[0:limit]

                productions.write({'state': 'draft'})
                productions.unlink()


            #                for production in productions:

                    # if r.cleanup_products_to_consume:
                    #     for m in production.move_lines:
                    #         move.write({'state': 'draft'})
                    #         m.unlink()
                    # if r.cleanup_consumed_products:
                    #     for m in production.move_lines2:
                    #         move.write({'state': 'draft'})
                    #         m.unlink()
                    # if r.cleanup_products_to_produce:
                    #     for m in production.move_created_ids:
                    #         move.write({'state': 'draft'})
                    #         m.unlink()
                    # if r.cleanup_produced_products:
                    #     for m in production.move_created_ids2:
                    #         move.write({'state': 'draft'})
                    #         m.unlink()
                    # if r.cleanup_scheduled_products:
                    #     for s in production.product_lines:
                    #         move.write({'state': 'draft'})
                    #         s.unlink()
                    # if r.cleanup_work_orders:
                    #     for w in production.workcenter_lines:
                    #         move.write({'state': 'draft'})
                    #         w.unlink()


            if r.cleanup_stock_moves:
                moves = self.env['stock.move'].search([])

                if r.limit:
                    limit = int(r.limit)
                    moves = moves[0:limit]
#                    move.write({'state': 'draft'})
                moves.unlink()
