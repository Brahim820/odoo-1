from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_journal(self):
        res = self.env['account.journal']

        inv_type = self._context.get('type', 'out_invoice')

        user = self.env.user

        # Refund invoices will keep the journal of the invoice.
        if user.default_sale_journal_id:
            if inv_type in ('out_invoice', 'out_refund'):
                res = user.default_sale_journal_id
        elif user.default_purchase_journal_id:
            if inv_type in ('in_invoice', 'in_refund'):
                res = user.default_purchase_journal_id

        if not res:
            res = super(AccountInvoice, self)._default_journal()

        return res

    journal_id = fields.Many2one(
        'account.journal',
        default=_default_journal)
