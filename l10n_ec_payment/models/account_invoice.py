# -*- coding: utf-8 -*-
import json
import time

from openerp import _, api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.v7
    def assign_outstanding_credit(self, cr, uid, id, credit_aml_id, context=None):
        move_line_obj = self.pool.get('account.move.line')
        credit_aml = move_line_obj.browse(cr, uid, credit_aml_id, context=context)
        if credit_aml.payment_id:
            credit_aml.payment_id.write({'invoice_ids': [(4, id, None)]})
        if context == None:
            context = {}
        context['check_move_validity'] = False
        invoice = self.browse(cr, uid, id)
        if credit_aml.payment_id.prepayment:
            if invoice.type == 'out_invoice':
                # Check to get invoice residual or aml
                aml_amount = abs(credit_aml.amount_residual) or credit_aml.credit
                if invoice.residual > aml_amount:
                    total_amount = aml_amount
                else:
                    total_amount = invoice.residual
                move = self.pool.get('account.move').create(cr, uid, {
                    'name': 'Prepago de %s' % (invoice.number),
                    'date': time.strftime('%Y-%m-%d'),
                    'ref': '',
                    'company_id': invoice.company_id.id,
                    'journal_id': credit_aml.payment_id.journal_id.id,
                    'partner_id': credit_aml.payment_id.partner_id.id,
                })
                debit_line = move_line_obj.create(cr, uid, {
                    'name': 'Prepago de %s' % (invoice.number),
                    'partner_id': credit_aml.payment_id.partner_id.id,
                    'move_id': move,
                    'debit': total_amount,
                    'credit': 0,
                    'account_id': credit_aml.account_id.id,
                    'payment_id': credit_aml.payment_id.id,
                }, context=context)
                credit_line = move_line_obj.create(cr, uid, {
                    'name': 'Prepago de %s' % (invoice.number),
                    'partner_id': credit_aml.payment_id.partner_id.id,
                    'move_id': move,
                    'credit': total_amount,
                    'debit': 0,
                    'account_id': invoice.account_id.id,
                    'payment_id': credit_aml.payment_id.id,
                }, context=context)
                # Reconcile the prepayment then the invoice
                move_line_obj.reconcile(cr, uid, [debit_line, credit_aml.id])
                # Post the entries
                self.pool.get('account.move').post(cr, uid, move)
                return self.browse(cr, uid, id, context=context).register_payment(move_line_obj.browse(cr, uid, credit_line))
            elif invoice.type == 'in_invoice':
                aml_amount = abs(credit_aml.amount_residual) or credit_aml.debit
                if invoice.residual > aml_amount:
                    total_amount = aml_amount
                else:
                    total_amount = invoice.residual
                move = self.pool.get('account.move').create(cr, uid, {
                    'name': 'Prepayment',
                    'date': time.strftime('%Y-%m-%d'),
                    'ref': '',
                    'company_id': invoice.company_id.id,
                    'journal_id': credit_aml.payment_id.journal_id.id,
                    'partner_id': credit_aml.payment_id.partner_id.id,
                })
                credit_line = move_line_obj.create(cr, uid, {
                    'name': 'Prepago de %s' % (invoice.number),
                    'partner_id': credit_aml.payment_id.partner_id.id,
                    'move_id': move,
                    'credit': total_amount,
                    'debit': 0,
                    'account_id': credit_aml.account_id.id,
                    'payment_id': credit_aml.payment_id.id,
                }, context=context)
                debit_line = move_line_obj.create(cr, uid, {
                    'name': 'Prepago de %s' % (invoice.number),
                    'partner_id': credit_aml.payment_id.partner_id.id,
                    'move_id': move,
                    'debit': total_amount,
                    'credit': 0,
                    'account_id': invoice.account_id.id,
                    'payment_id': credit_aml.payment_id.id,
                }, context=context)
                # Reconcile the prepayment then the invoice
                move_line_obj.reconcile(cr, uid, [credit_line, credit_aml.id])
                # Post the entries
                self.pool.get('account.move').post(cr, uid, move)
                return self.browse(cr, uid, id, context=context).register_payment(move_line_obj.browse(cr, uid, debit_line))

        else:
            return self.browse(cr, uid, id, context=context).register_payment(credit_aml)

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            # Allow add button to show on invoice during prepayment
            domain = [('journal_id.type', 'in', ('bank', 'cash')),
                      ('account_id.reconcile', '=', True),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(
                          self.partner_id).id),
                      ('reconciled', '=', False),
                      ('amount_residual', '!=', 0.0)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    # get the outstanding residual value in its currency. We don't want to show it
                    # in the invoice currency since the exchange rate between the invoice date and
                    # the payment date might have changed.
                    if line.currency_id:
                        currency_id = line.currency_id
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency_id = line.company_id.currency_id
                        amount_to_show = abs(line.amount_residual)
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    @api.multi
    def button_supplier_payments(self):
        context = {'tree_view_ref': 'account.view_account_supplier_payment_tree'}
        return {
            'name': _('PAGOS'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.payment_ids])],
            'context': context,
        }

    @api.multi
    def button_customer_payments(self):
        context = {'tree_view_ref': 'account.view_account_payment_tree'}
        return {
            'name': _('COBROS'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in self.payment_ids])],
            'context': context,
        }
