# -*- encoding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    event_id = fields.Many2one(compute="_compute_event_id", store=True, )

    @api.multi
    @api.depends('event_id')
    def _compute_event_id(self):
        for reg in self:
            event = reg.sale_order_id.event_id
            reg.event_id = event

            if event.event_ticket_ids:
                reg.event_ticket_id = event.event_ticket_ids[0]


class EventEvent(models.Model):
    _inherit = 'event.event'
   
    order_ids = fields.One2many(
        'sale.order', inverse_name='event_id',
        ondelete='restrict', string="Sale orders", )

    event_order_line = fields.One2many(
        'event.order.line', inverse_name='event_id',
        ondelete='set null', string="Sale order lines", )

    @api.multi
    def button_compute_so_qty_delivered(self):
        for event in self:
            if event.state == 'confirm':
                for so in event.order_ids:
                    so.button_compute_qty_delivered()


class SaleOrderLine(models.Model):
    _name = 'event.order.line'
    _description = 'Event Order Line'

    name = fields.Text(string='Description', required=True, )
    price_unit = fields.Float('Unit Price', required=True,
        digits=dp.get_precision('Product Price'), default=0.0, )
    product_uom_qty = fields.Float(string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1.0, )
    product_id = fields.Many2one('product.product', string='Product',
        domain=[('sale_ok', '=', True)], change_default=True,
        ondelete='restrict', required=True, )
    event_id = fields.Many2one('event.event', string='Event', )
