# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    asset_consumption_line_ids = fields.Many2many(
        'account.asset.asset.consumption',
        'asset_consumption_line_invoice_line_rel',
        'invoice_line_ids',
        'asset_consumption_line_ids',
        string='Asset consumption lines', )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic account', )



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_custom_attachments(self):
        try:
            res = super(AccountInvoice, self)._get_custom_attachments()
        except:
            res =[]
        lines = self.invoice_line_ids.mapped('asset_consumption_line_ids')
        for l in lines:
            if l.voucher:
                res.append(
                    (l.voucher_filename, l.voucher)
            )
        return res

