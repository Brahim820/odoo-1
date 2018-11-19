# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import UserError
import csv
from StringIO import StringIO

import base64


class AccountInvoiceImportWizard(models.TransientModel):
    _name = "account.invoice.import.wizard"

    text_to_import = fields.Text(string='Text to import', )
    file_to_import = fields.Binary(string='File to import', )
    invoice_creation_type = fields.Selection([
            ('individual','Individual Invoices'),
            ('group','Group by partner'),
        ], default="group",
        string='Group by',
        )
    header = fields.Boolean(string='The firts row is the header', )
    type = fields.Selection([
            ('out_invoice','Out invoice'),
            ('in_invoice','In invoice'),
            ('out_refund','Out refund'),
            ('in_refund','In refund'),
        ], default="out_invoice",
        string='Type',
    )

    auto_validate = fields.Boolean(
        string='Auto validate',
        default=True,
    )
    block_on_error = fields.Boolean(string='Block on error', default=True, )

    import_errors = fields.Text(string='Import errors', readonly=True, )
    state = fields.Selection([
            ('new','New'),
            ('done','Done'),
            ('fail','Fail'),
        ], default="new",
        string='State',
        )
    separator = fields.Selection([
            (',',','),
            (';',';'),
            ('|','|'),
        ], default=";",
        string='Separator',
        )
    invoices = fields.Char(string='Invoices', )

    @api.multi
    def _get_invoice_dict(self):
        import_errors = ""
        data = ""

        if self.file_to_import:
            data = base64.b64decode(self.file_to_import)
        if self.text_to_import:
            data += self.text_to_import

        if data == "":
            raise UserError(_("No lines to process."))

        lines = []
        row = 1
        for l in data.splitlines():
            if l == '':
                row += 1
                continue
            elif row == 1 and self.header:
                row += 1
                continue
            elif self.separator not in l:
                import_errors += _("No separator found on line: {} / {}\n").format(row, l[:60])
                row += 1
                continue
            try:
                vals = l.split(self.separator)
                vat = vals[0].strip("\"\'")
                default_code = vals[1].strip("\"\'")
                name = vals[2].strip("\"\'")
                price_unit = vals[3].strip("\"\'")
                quantity = vals[4].strip("\"\'")

                partner = self.env['res.partner'].search(
                    [
                        ('vat','=', vat),
                        ('parent_id','=', False)
                    ]
                )
                if len(partner) != 1:
                    import_errors += _(
                        "One partner should match id: {} on line {} / {}\n"
                    ).format(vat, row, l[:60])
                    row += 1
                    continue
                else:
                    if not partner.property_account_receivable_id:
                        import_errors += _(
                            "Partner {} has no receivable account.\n"
                        ).format(partner.name)
                product = self.env['product.product'].search(
                    [('default_code','=', default_code)]
                )
                if len(product) != 1:
                    import_errors += _(
                        "One product should match code: {} on line {} / {}\n"
                    ).format(default_code, row, l[:60])
                    row += 1
                    continue
                else:
                    if not product.property_account_income_id:
                        import_errors += _(
                            "Product {} has no income account.\n"
                        ).format(product.name)

                lines.append(
                    {
                        'partner': partner,
                        'product': product,
                        'vat': vat,
                        'default_code': default_code,
                        'name': name,
                        'price_unit': float(price_unit),
                        'quantity': float(quantity),
                    }
                )
            except:
                import_errors += _("Invalid format on line: {} / {}\n").format(row, l[:60])
            row += 1
        return lines, import_errors

    @api.multi
    def button_create_invoices(self):
        invoice = self.env['account.invoice']
        invoice_line = self.env['account.invoice.line']
        lines, import_errors = self._get_invoice_dict()

        if import_errors and self.block_on_error:
            self.write(
                {
                    'import_errors': import_errors,
                    'state': 'fail',
                }
            )
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice.import.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
                'context': self._context,
            }

        invoice_list = []
        for l in lines:
            product = l['product']
            partner = l['partner']

            invoice_vals = next(
                (item for item in invoice_list
                    if item["partner_id"] == partner.id), False
            )

            if not invoice_vals or self.invoice_creation_type == 'individual':
                account = product.property_account_income_id \
                    or product.categ_id.property_account_income_categ_id
                tax_ids = product.taxes_id.ids
                line_ids = [product.id]

                invoice_list.append(
                    {
                        'partner_id': partner.id,
                        'type': self.type,
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

        invoices = []
        for inv in invoice_list:
            new_invoice = self.env['account.invoice'].create(inv)
            invoices.append(str(new_invoice.id))
            if self.auto_validate:
                new_invoice.signal_workflow('invoice_open')

        self.write(
            {
                'import_errors': import_errors or _("Import finished with no errors"),
                'state': 'done',
                'invoices': ','.join(invoices),
            }
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.import.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def button_close(self):
        invoices = self.invoices
        context = {
            'tree_view_ref': 'account.invoice_tree',
            'form_view_ref': 'account.invoice_form',
        }
        return {
            'name': _('INVOICES'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [int(x) for x in invoices.split(',')])],
            'context': context,
        }

