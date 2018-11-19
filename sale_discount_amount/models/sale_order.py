# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_discount = fields.Monetary(
        # digits=dp.get_precision('Product Price'),
        compute='_compute_price_discount',
        string='Price discount',
        readonly=True, store=True, )

    def get_price_without_discounts(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit
        taxes = False
        if self.tax_id:
            taxes = self.tax_id.compute_all(
                price, currency, self.quantity, product=self.product_id,
                partner=self.invoice_id.partner_id
            )
            price_without_discounts = taxes['total_excluded'] if taxes else self.quantity * price
        if (
            self.invoice_id.currency_id and
            self.invoice_id.company_id and
            self.invoice_id.currency_id != self.invoice_id.company_id.currency_id
        ):
            price_without_discounts = self.invoice_id.currency_id.with_context(
                date=self.invoice_id.date_invoice).compute(
                    price_without_discounts, self.invoice_id.company_id.currency_id
            )
        return price_without_discounts

    @api.depends('product_uom_qty', 'discount', 'price_unit','price_subtotal')
    def _compute_price_discount(self):
        """
        Compute the amounts of the price discount.
        """
        for line in self:
            # diff_cents = (round(line.price_unit, 2) * line.quantity) - \
            #     (line.price_unit * line.quantity)
            price = line.product_uom_qty * line.price_unit
            if any(tax.price_include for tax in line.tax_id):
                price = line.get_price_without_discounts()

            # discount = price - (line.price_subtotal + diff_cents)
            discount = price - line.price_subtotal
            line.update({
                'price_discount': abs(discount),
            })


class SaleOrder(models.Model):
    _inherit = "sale.order"

    price_discount = fields.Monetary(
        # digits=dp.get_precision('Product Price'),
        compute='_compute_price_discount',
        string='Price discount',
        readonly=True, store=True, )

    @api.depends('order_line.price_discount')
    def _compute_price_discount(self):
        for order in self:
            order.price_discount = sum(order.order_line.mapped('price_discount'))
