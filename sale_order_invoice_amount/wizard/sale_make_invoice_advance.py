# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp import exceptions

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(selection_add=[('amount', 'Fixed amount distributed in lines')])

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'amount':
            if self.amount > 0:
                amount = self.amount
            else:
                raise exceptions.UserError(_('There is no amount to invoice'))
            sale_orders.action_invoice_create_from_amount(grouped=False, amount=amount)
            if self._context.get('open_invoices', False):
                return sale_orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}

        else:
            res = super(SaleAdvancePaymentInv,self).create_invoices()
            return res
