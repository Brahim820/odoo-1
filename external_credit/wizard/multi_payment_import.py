# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import base64


class MultiPaymentImportWizard(models.TransientModel):
    _name = "multi.payment.import.wizard"

    text = fields.Text(string='Text', )

    file_to_import = fields.Binary(string='File', attachment=True, )

    """
    @api.multi
    def _get_file_dict(self):
        if self.file_to_import:
            file_payments = base64.b64decode(self.file_to_import)
        else:
            file_payments = ''

        payments = file_payments

        lines = []
        for l in payments.splitlines():
            if l == '':
                continue
            if ',' in l:
                vals = l.split(',')
                code, discount = vals[0], vals[1]

            else:
                code, discount = l, 1

            lines.append({
                'code': vat,
                'discount': discount,
            })

        return lines
    @api.multi
    def button_create_invoices(self):
        invoice = self.env['account.invoice']
        invoice_line = self.env['account.invoice.line']
        lines = self._get_invoice_dict()

        invoice_list = []
        for l in lines:

            partner = self.env['res.partner'].search(
                [('vat','=', l['vat'])]
            )

            product = self.env['product.product'].search(
                [('default_code','=', l['default_code'])]
            )
            if not partner:
                raise UserError(_(
                    "No se ha podido localizar el cliente con identificación: %s",
                    l['vat']
                ))

            if not product:
                raise UserError(_(
                    "No se ha podido localizar el producto con código: %s",
                    l['default_code']))

            invoice_vals = next((item for item in invoice_list\
                                if item["partner_id"] == partner.id), False)
            if not invoice_vals or self.invoice_creation_type == 'individual':
                account = product.property_account_income_id \
                    or product.categ_id.property_account_income_categ_id
                tax_ids = product.taxes_id.ids
                line_ids = [product.id]

                invoice_list.append(
                    {
                        'partner_id': partner.id,
                        'invoice_line_ids': [
                            (0, 0,
                            {
                                'product_id': product.id,
                                'uom_id': product.uom_id.id,
                                'name': l['name'],
                                'price_unit': l['price_unit'],
                                'quantity': l['quantity'],
                                'account_id': account.id,
                                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                            }
                            )
                        ]
                    }
                )

            else:
                invoice_vals['invoice_line_ids'].append((0, 0,
                            {
                                'product_id': product.id,
                                'name': l['name'],
                                'price_unit': l['price_unit'],
                                'quantity': l['quantity'],
                                'uom_id': product.uom_id.id,
                                'account_id': account.id,
                                'invoice_line_tax_ids': [(6, 0, tax_ids)],
                            }
                        )
                    )

        for inv in invoice_list:
            new_invoice = self.env['account.invoice'].create(inv)
            if self.auto_validate:
                new_invoice.signal_workflow('invoice_open')
    """
