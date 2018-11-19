# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import  models 


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    def inv_line_characteristic_hashcode(self, invoice_line):
        """
        No need to use super as we need only the hashcode we generate.
        """
        journal = self.journal_id
        res = ''.join([
            journal.group_by_account_id and str(invoice_line['account_id']) or '',
            journal.group_by_tax_ids and str(invoice_line.get('tax_ids', 'False')) or '',
            journal.group_by_tax_line_id and str(invoice_line.get('tax_line_id', 'False')) or '',
            journal.group_by_product_id and str(invoice_line.get('product_id', 'False')) or '',
            journal.group_by_analytic_account_id and str(invoice_line.get('analytic_account_id', 'False')) or '',
            journal.group_by_date_maturity and str(invoice_line.get('date_maturity', 'False')) or '',
            ])
        return res

