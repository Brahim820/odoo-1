# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class StockWarehouseOrderPoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    line_ids = fields.One2many('stock.orderpoint.line', 'orderpoint_id', 'Lines')


class StockOrderPointLine(models.Model):
    """
    Recompute StockWarehouse order point
    """

    _name = 'stock.orderpoint.line'
    _description = __doc__
    _order = 'date desc'

    @api.multi
    def compute_orderpoint(self, product_ids=None):
        # TODO: Implement function
        print self
        for rec in self:
            print rec

    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'OrderPoint', required=True,)
    previous_min_qty = fields.Float(
        'Previous Minimum Quantity', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="This is the previous min qty ")
    previous_max_qty = fields.Float(
        'Previous Maximum Quantity', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="This is the previous max qty")
    suggested_min_qty = fields.Float(
        'Suggested Minimum Quantity', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="Suggested new previous_min_qtymin qty")
    suggested_max_qty = fields.Float(
        'Suggested Maximum Quantity', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="Suggested new max qty")
    reason = fields.Text('Reason')
    date = fields.Date('Date')
    state = fields.Selection(
        [('new', 'New'), ('approved', 'Approved'), ('rejected', 'Rejected')], 'State', default='new')

    @api.one
    def button_approve(self):
        """ Approve change"""
        self.orderpoint_id.product_min_qty = self.suggested_min_qty
        self.orderpoint_id.product_max_qty = self.suggested_max_qty
        self.state = 'approved'

    @api.one
    def button_reject(self):
        """ Reject change"""
        self.state = 'rejected'
