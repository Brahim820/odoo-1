# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('inventory_line_id')
    def _compute_theoretical_qty(self):
        for r in self:
            if r.inventory_line_id:
                r.theoretical_qty = r.inventory_line_id.theoretical_qty
            else:
                r.theoretical_qty = r.actual_qty

    # Computed field to use on views.
    @api.multi
    @api.onchange('theoretical_qty', 'actual_qty')
    def _onchange_difference(self, diff=False):
        if self.theoretical_qty != self.actual_qty:
            diff = True
        self.has_difference = diff

    has_difference = fields.Boolean('The actual and theorical qty are different.', )

    theoretical_qty = fields.Float('Theoretical Qty', digits=(9,2), compute=_compute_theoretical_qty, store=False,)
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
    def action_confirm(self):
        for r in self:
            for m in r.move_lines:
                if m.theoretical_qty == m.actual_qty:
                    m.inventory_line_id.unlink()
                else:
                    m.inventory_line_id.write({
                        'product_qty': m.actual_qty,
                        'reason': m.reason,
                    })

            super(StockPicking, self).action_confirm()

    @api.multi
    def button_create_move_lines_from_template(self, **kwargs):
        if self.inventory_id:
            inventory = self.inventory_id
        else:
            name = self.location_dest_id.display_name + ' ' + str(fields.datetime.now())[0:16]
            inventory = self.env['stock.inventory'].create({
                'name': name,
                'location_id': self.location_dest_id.id,
                'filter': 'partial',
            })

            self.write({
                'inventory_id': inventory.id,
            })

        super(StockPicking, self).button_create_move_lines_from_template()
        inventory.prepare_inventory()

        # TODO: optimizar estos cálculos.
        for line in inventory.line_ids:
            line.product_qty = line.theoretical_qty

        for line in self.move_lines:
            line.actual_qty = line.theoretical_qty

    @api.multi
    def prepare_move_lines_from_template(self, t, expected_date):
        # TODO: permitir inventariar pedidos con líneas ingresadas previamente.
        if self.move_lines:
            raise exceptions.UserError(_('El pedido debe estar vacío para poder ejecutar el inventario.'))

        vals = super(StockPicking, self).prepare_move_lines_from_template(t=t, expected_date=expected_date)

        inventory_line = self.env['stock.inventory.line'].create({
            'inventory_id': self.inventory_id.id,
            'product_id': vals['product_id'],
            'location_id': vals['location_dest_id'],
        })

        _logger.info('Inventory Line: %s', inventory_line)

        vals.update({
            'inventory_line_id': inventory_line.id,
        })


        return vals

    inventory_id = fields.Many2one('stock.inventory', string="Inventory", copy=False, )
