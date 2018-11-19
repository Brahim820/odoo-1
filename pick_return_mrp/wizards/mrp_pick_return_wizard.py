# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import _, api, exceptions, fields, models
from openerp.tools.float_utils import float_round


class MrpPickReturnWizard(models.TransientModel):
    _name = "mrp.pick.return.wizard"
    _inherit = 'pick.return.wizard'
    _description = "Create picking for the MO"

    mo_id = fields.Many2one(
        'mrp.production', 'Production', required=True, readonly=True, )
    pick_return_line_ids = fields.One2many(
        'pick.return.wizard.line',
        'mrp_wizard_id',
        string='Moves to execute',
        ondelete='cascade',
    )

    @api.onchange('type', 'route_id')
    def _onchange_route_id(self):
        # The src of the MO is the dest of the picking.
        loc_dest = self.mo_id.location_src_id
        origin = self.mo_id.name
        if loc_dest and self.route_id:
            dest, src, trans, out_type, in_type = self._prepare_locations(loc_dest=loc_dest)

            vals = {
                'origin': origin,
                'location_dest_id': dest.id,
                'location_src_id': src.id,
                'location_trans_id': trans.id,
                'out_picking_type_id': out_type.id,
                'in_picking_type_id': in_type.id,
            }
            self.update(vals)

    @api.multi
    def mrp_create_move_lines(self):
        mo = self.mo_id
        uom = self.env['product.uom']

        type = self._context.get('type')

        move_lines = self.env['stock.move']

        if type == 'leftover':
            raw_pickings = self.mo_id.raw_picking_ids.filtered(lambda x: x.state == 'done')

            product_ids = raw_pickings.mapped('pack_operation_product_ids.product_id')
            finished_ids = mo.move_created_ids2.mapped('product_id')
            raw_ids = product_ids - finished_ids
            pick_ids = raw_pickings.filtered(lambda x: x.location_dest_id == mo.location_src_id)
            return_ids = raw_pickings.filtered(lambda x: x.location_id == mo.location_src_id)
            consumed_ids = mo.move_lines2.filtered(lambda x: x.state == 'done')

            lines = []
            for rm in raw_ids:
                pick_op = pick_ids.mapped('pack_operation_product_ids').filtered(
                    lambda x: x.product_id == rm)
                return_op = return_ids.mapped('pack_operation_product_ids').filtered(
                    lambda x: x.product_id == rm)
                consumed_quants = consumed_ids.mapped(
                    'quant_ids').filtered(lambda x: x.product_id == rm)

                pick_qty = sum(pick_op.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.qty_done,
                    rm.uom_id.id
                )))

                return_qty = sum(return_op.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.qty_done,
                    rm.uom_id.id
                )))

                consumed_qty = sum(consumed_quants.mapped(lambda line: uom._compute_qty(
                    line.product_uom_id.id,
                    line.qty,
                    rm.uom_id.id
                )))

                uom_qty = pick_qty - return_qty - consumed_qty
                if uom_qty > 0:
                    lines.append({
                        'product_id': rm.id,
                        'product_uom': rm.uom_id.id,
                        'product_uom_qty': uom_qty,
                        'mrp_wizard_id': self.id,
                    })
        else:
            if type == 'raw':
                move_lines = mo.move_lines
            elif type == 'cancel':
                move_lines = mo.move_lines2.filtered(lambda x: x.state == 'cancel')
            elif type == 'finished':
                move_lines = mo.move_created_ids2.filtered(lambda x: x.state == 'done')

            lines = []
            for line in move_lines:
                lines.append({
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_uom_qty': line.product_uom_qty,
                    'mrp_wizard_id': self.id,
                    'type': type,
                })

        self.create_pick_return_lines(lines=lines)

    @api.multi
    def action_mrp_create_move_lines(self):
        self.mrp_create_move_lines()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.pick.return.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }


class PickReturnWizardLine(models.TransientModel):
    _inherit = "pick.return.wizard.line"

    mrp_wizard_id = fields.Many2one('mrp.pick.return.wizard', string='Pick return wizard', )
    product_unreserved = fields.Float(
        compute='_compute_product_qty_unreserved', string=('Product Available'), defaults=0.00, digits=dp.get_precision('Product Unit of Measure'))
    type = fields.Char('Type')

    @api.multi
    def _compute_product_qty_unreserved(self):
        quant_obj = self.env['stock.quant']
        for row in self:
            location = row.mrp_wizard_id.location_dest_id.id if row.type == 'raw' else row.mrp_wizard_id.location_src_id.id
            quant_data = quant_obj.search(
                [('product_id', '=', row.product_id.id),
                 ('location_id', '=', location),
                 ('reservation_id', '=', False)])
            quant = sum([x.qty for x in quant_data]) if len(quant_data) > 0 else 0.00
            row.product_unreserved = quant
