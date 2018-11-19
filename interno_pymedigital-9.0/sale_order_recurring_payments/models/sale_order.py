# -*- encoding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_begin = fields.Date(
        string="Recurring Payment's start date",
        help="If selected, all recurring payments will use this date to compute the overdue payments.", )

    @api.multi
    def button_compute_qty_delivered(self, date_begin=False):
        for order in self:
            fmt = '%Y-%m-%d'
            today = fields.Date.from_string(fields.Date.today())
            for line in order.order_line.filtered(lambda l: l.product_id.recurring):
                date_begin = line.date_begin or order.date_begin or date_begin
                if not date_begin:
                    raise UserError(_("Es necesario configurar una fecha de inicio"))

                delivered = (fields.Date.from_string(date_begin) - today).days
                if line.product_id.in_advance:
                    days_to_invoice = line.product_id.frequency + abs(int(delivered))
                else:
                    days_to_invoice = abs(int(delivered))
                to_invoice = days_to_invoice / line.product_id.frequency

                if line.product_uom_qty > to_invoice:
                    line.qty_delivered = to_invoice
                else:
                    line.qty_delivered = line.product_uom_qty

    # @api.multi
    # def button_compute_qty_delivered(self, date_begin=False):
    #     for order in self:
    #         fmt = '%Y-%m-%d'
    #         if order.date_begin:
    #             date_begin = datetime.strptime(order.date_begin[0:10], fmt)
    #         else:
    #             date_begin = datetime.strptime(date_begin[0:10], fmt)
    #
    #         if date_begin:
    #             today = fields.datetime.now()
    #             delivered = (date_begin - today).days
    #
    #         for line in order.order_line.filtered(lambda l: l.product_id.recurring):
    #             if line.product_id.in_advance:
    #                 days_to_invoice = line.product_id.frequency + abs(int(delivered))
    #             else:
    #                 days_to_invoice = abs(int(delivered))
    #
    #             to_invoice = days_to_invoice / line.product_id.frequency
    #             if line.product_uom_qty > to_invoice:
    #                 line.qty_delivered = to_invoice
    #             else:
    #                 line.qty_delivered = line.product_uom_qty


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_begin = fields.Date(
        string="Recurring Payment's start date",
        help="If selected, all recurring payments will use this date to compute the overdue payments.", )
