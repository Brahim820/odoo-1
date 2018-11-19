# -*- encoding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.tools import float_is_zero
from openerp.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create_from_amount(self, grouped=False, amount=0):
        if amount == 0:
            raise UserError(_('The amount to invoice should be greater than cero.'))

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            inv_obj = self.env['account.invoice']
            invoices = {}

            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice):
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', '):
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)

                discount = 1 - (line.discount or 0.0 / 100.0)
                if line.price_unit > 0 and discount < 100:
                    paid_qty = amount / (line.price_unit * discount)
                else:
                    paid_qty = line.product_uom_qty

                to_invoice = 0
                if line.qty_to_invoice > 0:
                    if paid_qty >= line.qty_to_invoice:
                        to_invoice = line.qty_to_invoice
                    else:
                        to_invoice = paid_qty

                name = line.name + ' desde ' + str(round(line.qty_invoiced, 2)) + ' a ' + str(
                    round(line.qty_invoiced + to_invoice, 2)) + ' de ' + str(round(line.product_uom_qty, 2))

                line.invoice_line_create_from_amount(invoices[group_key].id, to_invoice, name)
                amount -= to_invoice * line.price_unit

            if amount > 0:
                discount = 1 - (line.discount or 0.0 / 100.0)
                lines = order.order_line.filtered(lambda l: l.product_uom_qty - l.qty_invoiced > 0)
                for line in lines.sorted(
                        key=lambda l: (l.product_uom_qty - l.qty_invoiced) * l.price_unit):
                    if line.price_unit > 0 and discount < 100:
                        paid_qty = amount / (line.price_unit * discount)
                    else:
                        paid_qty = line.product_uom_qty
                    residual_qty = line.product_uom_qty - line.qty_invoiced

                    to_invoice = 0
                    if residual_qty > 0:
                        if round(paid_qty, 5) > round(residual_qty, 5):
                            to_invoice = residual_qty
                        else:
                            to_invoice = paid_qty

                    name = ' Pago anticipado: ' + line.name + ' desde ' + str(round(line.qty_invoiced, 2)) + ' a ' + str(
                        round(line.qty_invoiced + to_invoice, 2)) + ' de ' + str(round(line.product_uom_qty, 2))
                    line.invoice_line_create_from_amount(invoices[group_key].id, to_invoice, name)
                    amount -= to_invoice * line.price_unit

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()

        #TODO: agregar este cálculo a la función principal
        # para evitar problemas con las funciones que hacen super
        # como en el módulo l10n_ec_sri_sale
        resx = [inv.id for inv in invoices.values()]
        invx = self.env['account.invoice'].browse(resx)
        for i in invx:
            i.compute_sri_invoice_amounts()

        return [inv.id for inv in invoices.values()]


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def invoice_line_create_from_amount(self, invoice_id, qty, name):
        """
        Create an invoice line. The quantity to invoice can be positive (invoice) or negative
        (refund).

        :param name: char
        :param invoice_id: integer
        :param qty: float quantity to invoice
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'name': name, 'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])]})
                self.env['account.invoice.line'].create(vals)
