# -*- coding: utf-8 -*-
from openerp import models, fields, api


class SriTaxFormSet(models.Model):
    _inherit = ['l10n_ec_sri.tax.form.set']

    @api.multi
    def button_sri_ats_checker(self):
        for s in self:

            invoices = s.in_invoice_ids + s.in_refund_ids
            invoices += s.out_invoice_ids + s.out_refund_ids
            for inv in invoices:
                inv.get_ats_errors()

