# -*- encoding: utf-8 -*-
from openerp import api, fields, models, _
from datetime import datetime
from openerp.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def button_compute_qty_delivered(self):
        for order in self:
            date_begin = order.event_id.date_begin
            for line in order.order_line.filtered(lambda l: l.product_id.event_ok):
                line.qty_delivered = line.product_uom_qty
            super(SaleOrder, self).button_compute_qty_delivered(date_begin)

    event_id = fields.Many2one(
        comodel_name='event.event', string='Evento', )
    registration_ids = fields.One2many(
        'event.registration', inverse_name='sale_order_id',
        ondelete='restrict', string="Registros", )

    @api.multi
    @api.onchange('event_id')
    def _onchange_event_id(self):
        for order in self:
            event = order.event_id

            lines = []
            for line in event.event_order_line:
                if line.product_id.event_ok:
                    raise UserError(u'Las inscripciones deben ser ingresadas en la pestaña de TICKETS')
                vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'tax_id': line.product_id.taxes_id,
                    'product_uom_qty': line.product_uom_qty,
                    'name': line.name,
                    'price_unit': line.price_unit,
                    'order_id': order.id,
                }
                lines.append((0,0,vals))
            for line in event.event_ticket_ids:
                vals = {
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'tax_id': line.product_id.taxes_id,
                    'event_ticket_id': line.id,
                    'product_uom_qty': 1,
                    'name': line.name,
                    'price_unit': line.price,
                    'order_id': order.id,
                }
                lines.append((0,0,vals))

            order.order_line = lines

    @api.multi
    @api.depends('order_line', 'order_line.qty_delivered', 'order_line.qty_invoiced', 'invoice_ids')
    def _compute_pending_total(self):
        for r in self:
            amount_total = r.amount_total

            invoiced = sum(r.mapped('invoice_ids').mapped('amount_total'))
            # Valor total pendiente de facturar.
            r.pending = amount_total - invoiced

            to_invoice = 0
            for line in r.order_line:

                tax_obj = self.env['account.tax']
                tax_dict = tax_obj.compute_all(
                    line.price_unit,
                    r.currency_id,
                    line.qty_delivered,
                    product=line.product_id,
                    partner=r.partner_id
                )

                to_invoice += tax_dict.get('total_included', 0)
            # Valor pendiente de facturar.
            r.pending_to_invoice = to_invoice - invoiced

    pending = fields.Float('SO Pending', compute=_compute_pending_total, store=True, digits=(9, 2), )
    pending_to_invoice = fields.Float('Pending to invoice', compute=_compute_pending_total, store=True, digits=(9, 2), )

    def _prepare_invoice(self):
        """
        copy registration data to name field on invoice
        """
        invoice = super(SaleOrder, self)._prepare_invoice()
        if self.registration_ids:
            name = ''
            for reg in self.registration_ids:
                if name and reg.name not in name.split(', '):
                    name += ', ' + reg.name or ''
                else:
                    name += reg.name or ''
            invoice['name'] = name
        return invoice


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    event_id = fields.Many2one(
        comodel_name='event.event', string='Evento',
        compute="_compute_event_id", )

    @api.multi
    @api.depends('product_id')
    def _compute_event_id(self):
        for r in self:
            if r.product_id.event_ok:
                r.event_id = r.order_id.event_id

    @api.multi
    @api.onchange('event_id', 'product_id')
    def _onchange_ticket_id(self):
        for r in self:
            if r.product_id.event_ok and r.event_id.event_ticket_ids:
                r.event_ticket_id = r.event_id.event_ticket_ids[0]
            if r.product_id and not r.product_id.event_ok:
                r.event_ticket_id = []
