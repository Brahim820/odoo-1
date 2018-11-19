# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import _, api, exceptions, fields, models


class StockLocationKardexLine(models.Model):
    _name = 'stock.location.kardex.line'
    _order = 'sequence'

    kardex_id = fields.Many2one(
        'stock.location.kardex', ondelete='restrict', string="Product kardex", )
    sequence = fields.Integer(string='Sequence ', )
    date = fields.Datetime(string='Date', )
    name = fields.Char(string='Name', )
    in_qty = fields.Float('In qty', digits_compute=dp.get_precision('Product Unit of Measure'), )
    out_qty = fields.Float('Out qty', digits_compute=dp.get_precision('Product Unit of Measure'), )
    balance_qty = fields.Float(
        'Balance qty', digits_compute=dp.get_precision('Product Unit of Measure'), )
    previous_balance_qty = fields.Float(
        'Previous balance qty', digits_compute=dp.get_precision('Product Unit of Measure'), )
    move_id = fields.Many2one('stock.move', string='Move', )
    picking_id = fields.Many2one('stock.picking', string='Picking', )
    related_move_id = fields.Many2one('stock.move', string='Related move', )
    counterpart_location_id = fields.Many2one('stock.location', string='Related Location', )
    transit_location_id = fields.Many2one('stock.location', string='Transit Location', )
    in_value = fields.Float(string='In value', )
    out_value = fields.Float(string='Out value', )
    previous_balance_value = fields.Float(string='Previous value', )
    balance_value = fields.Float(string='Balance value', )


class StockLocationKardex(models.Model):
    _name = 'stock.location.kardex'

    location_id = fields.Many2one('stock.location', string='Location',
                                  domain=[('usage', '=', 'internal')],)
    product_id = fields.Many2one(
        'product.product', ondelete='set null', string="Product",
        required=True, )
    balance_qty = fields.Float(
        'Balance qty', digits_compute=dp.get_precision('Product Unit of Measure'), )
    balance_value = fields.Float('Inventory value', )
    kardex_line_ids = fields.One2many(
        'stock.location.kardex.line', 'kardex_id', string='Kardex lines', )
    sequence = fields.Integer(string='Sequence', )

    @api.multi
    def prepare_kardex_line_dict(self, move, balance, value, sequence):
        related_move = self.env['stock.move']
        transit_location = self.env['stock.location']
        counterpart_location = self.env['stock.location']
        in_value = out_value = 0.00
        in_qty = out_qty = 0

        move_value = sum(move.mapped('quant_ids.inventory_value'))
        if self.location_id == move.location_dest_id:
            in_value = move_value
            in_qty = move.product_qty
            balance_value = value + move_value
            balance_qty = balance + move.product_qty
            related_move = move.find_move_ancestors(move)
            if not related_move:
                counterpart_location = move.location_id
            else:
                related_move = self.env['stock.move'].browse(related_move[0])
                if self.location_id == related_move.location_id:
                    counterpart_location = move.location_id
                else:
                    transit_location = move.location_id
                counterpart_location = related_move.location_id
        elif self.location_id == move.location_id:
            out_value = move_value
            out_qty = move.product_qty
            balance_value = value - move_value
            balance_qty = balance - move.product_qty
            related_move = move.move_dest_id
            if not related_move:
                counterpart_location = move.location_dest_id
            elif self.location_id == related_move.location_dest_id:
                counterpart_location = move.location_dest_id
            else:
                transit_location = move.location_dest_id
                counterpart_location = related_move.location_dest_id
        try:
            related_move_id = related_move.id
        except:
            related_move_id = False

        vals = {
            'kardex_id': self.id,
            'sequence': sequence,
            'date': move.date,
            'name': move.origin or move.name,
            'move_id': move.id,
            'picking_id': move.picking_id.id,
            'related_move_id': related_move_id,
            'in_qty': in_qty,
            'out_qty': out_qty,
            'balance_qty': balance_qty,
            'previous_balance_qty': balance,
            'in_value': in_value,
            'out_value': out_value,
            'balance_value': balance_value,
            'previous_balance_value': value,
            'transit_location_id': transit_location.id or False,
            'counterpart_location_id': counterpart_location.id or False,
        }

        return vals, balance_qty, balance_value

    @api.multi
    def button_update_kardex(self, moves=False):
        sequence = self.sequence
        if not moves or isinstance(moves, dict):
            start_date = '2000-01-01 00:00:00'
            if self.kardex_line_ids:
                start_date = self.kardex_line_ids.filtered(lambda x: x.sequence == sequence).date
            moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('date', '>', start_date),
                ('product_id', '=', self.product_id.id),
                '|',
                ('location_dest_id', '=', self.location_id.id),
                ('location_id', '=', self.location_id.id)
            ]).sorted(lambda x: x.date)

        balance = self.balance_qty
        value = self.balance_value
        for move in moves:
            sequence += 1
            vals, balance_qty, balance_value = self.prepare_kardex_line_dict(
                move, balance, value, sequence)
            self.env['stock.location.kardex.line'].create(vals)
            balance = balance_qty
            value = balance_value

        self.balance_qty = balance
        self.balance_value = value
        self.sequence = sequence


class StockLocation(models.Model):
    _inherit = 'stock.location'

    kardex_ids = fields.One2many(
        'stock.location.kardex',
        'location_id',
        string='Kardex',
    )

    @api.multi
    def create_kardex(self):
        products = self.env['product.product'].search([('type', '=', 'product')])
        created_products = self.kardex_ids.mapped('product_id')
        new_products = products - created_products

        for p in new_products:
            self.env['stock.location.kardex'].create({
                'product_id': p.id,
                'location_id': self.id,
            })

    @api.multi
    def button_update_kardex(self):
        self.create_kardex()
        kardex = self.kardex_ids
        for k in kardex:
            k.button_update_kardex()

