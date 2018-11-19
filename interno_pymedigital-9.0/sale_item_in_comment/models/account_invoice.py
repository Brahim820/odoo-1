# -*- coding: utf-8 -*-
import StringIO

from openerp import _, api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        res = super(AccountInvoice, self)._onchange_invoice_line_ids()

        items = ''.join([
            "ITEMS: ",
            str(sum(self.invoice_line_ids.mapped('quantity')))
        ])
        comment = self.comment or ''

        if comment == '':
            self.comment = items
        elif 'ITEMS:' not in comment:
            self.comment = comment + "\n" + items
        elif 'ITEMS:' in comment:
            c = u""
            s = StringIO.StringIO(comment)
            for line in s:
                if 'ITEMS:' in line:
                    c += items
                else:
                    c += line
            self.comment = c
            return res

