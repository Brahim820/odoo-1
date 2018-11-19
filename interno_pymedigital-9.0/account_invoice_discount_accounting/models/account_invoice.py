# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for line in self.invoice_line_ids:
            if not line.price_discount:
                continue

            iml = [r for r in res if r.get('invl_id') == line.id]
            iml = iml[0]
            iml.update({'price': iml['price'] + line.price_discount,})

            """
            # Este método crea una línea separada para el descuento.
            src_discount_move_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': _('Price discount ') + line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.price_discount,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                #'tax_ids': tax_ids,
                'invoice_id': self.id,
            }
            #if line['account_analytic_id']:
            #    move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(src_discount_move_dict)
            """
            dest_discount_move_dict = {
                'type': 'dest',
                'name': _('Discount expense ') + line.name.split('\n')[0][:64],
                'price': -line.price_discount,
                'account_id': line.get_discount_account().id,
                'invoice_id': self.id,

                #'date_maturity': inv.date_due,
                #'amount_currency': diff_currency and total_currency,
                #'currency_id': diff_currency and inv.currency_id.id,
                #'quantity': line.quantity,
                #'price': line.price_discount,
                #'product_id': line.product_id.id,
                #'uom_id': line.uom_id.id,
                #'account_analytic_id': line.account_analytic_id.id,
            }
            #if line['account_analytic_id']:
            #    move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(dest_discount_move_dict)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def get_discount_account(self):
        res = self.account_id
        if self.invoice_id.type in ('in_invoice','in_refund'):
            res = self.company_id.purchase_discount_account_id or res
        else:
            res = self.company_id.sale_discount_account_id or res

        return res


