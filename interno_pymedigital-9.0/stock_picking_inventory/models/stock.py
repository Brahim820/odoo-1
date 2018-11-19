# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class StockMove(models.Model):
    _inherit = 'stock.move'

    theoretical_qty = fields.Float('Theoretical Qty', digits=(9,2), readonly=True, )
    actual_qty = fields.Float('Actual Qty', digits=(9,2), )
    inventory_line_id = fields.Many2one('stock.inventory.line', string="Line", copy=False, )
    reason = fields.Selection([('scrap', 'Desperdicio'),
                               ('broken', 'Ruptura o daño'),
                               ('client', 'Reclamo de cliente'),
                               ('unknown', 'Desconocido'),
                               ('unregistered', 'Ventas sin registrar'),
                             ],
                              string='Reason', )


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    reason = fields.Selection([('scrap', 'Desperdicio'),
                               ('broken', 'Ruptura o daño'),
                               ('client', 'Reclamo de cliente'),
                               ('unknown', 'Desconocido'),
                               ('unregistered', 'Ventas sin registrar'),
                             ],
                              string='Reason', )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def remove_no_diff_inventory_lines(self):
        no_diff = self.env['stock.inventory.line']
        for m in self.move_lines:
            if m.theoretical_qty == m.actual_qty:
                no_diff += m.inventory_line_id
            else:
                m.inventory_line_id.write({
                    'product_qty': m.actual_qty,
                    'reason': m.reason,
                })
        no_diff.unlink()

        if not self.inventory_id.line_ids:
            self.inventory_id.unlink()


    @api.multi
    def create_inventory_from_picking(self):
        for r in self:
            location = r.location_dest_id.id

            if r.inventory_id:
                inventory = r.inventory_id
                if inventory.state == 'confirm':
                    inventory.action_cancel_inventory()
                elif inventory.state in ('pending','done'):
                    raise UserError(_(
                        "You cannot create a new inventory as this picking already has a inventory pending to aprobe or aprobed."))
                # TODO: cancelar y rehacer el inventario.
            else:
                name = r.location_dest_id.display_name + str(r.min_date)
                inventory = self.env['stock.inventory'].create({
                    'date': fields.Datetime.now(),
                    'name': name,
                    'location_id': location,
                    'filter': 'partial',
                })

                r.write({
                    'inventory_id': inventory.id,
                })

            for m in r.move_lines:
                inventory_line = self.env['stock.inventory.line'].create({
                    'inventory_id': r.inventory_id.id,
                    'product_id': m.product_id.id,
                    'location_id': location,
                })

                m.write({
                    'inventory_line_id': inventory_line.id,
                    'theoretical_qty': inventory_line.theoretical_qty,
                    'actual_qty': inventory_line.theoretical_qty,
                })

            inventory.prepare_inventory()

    inventory_id = fields.Many2one('stock.inventory', string="Inventory", copy=False, )
