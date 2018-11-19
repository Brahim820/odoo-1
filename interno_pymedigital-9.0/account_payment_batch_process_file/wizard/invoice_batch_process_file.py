#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import cStringIO
import csv
import re
import StringIO

from openerp import _, api, fields, models
from openerp.exceptions import UserError

INV_TO_PARTN = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or
# goes out
INV_TO_PAYM_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class AccountPaymentBatchFile(models.TransientModel):
    _name = "account.payment.batch.file"

    partner_id = fields.Many2one('res.partner', string=_('Partner'))
    payment_method_id = fields.Many2one('account.payment.method',
                                        string='Payment Type')
    csv_file = fields.Binary(_('CSV File'))
    delimiter = fields.Char(_('Delimiter'), default=',')
    csv_name = fields.Char(_('CSV File name'))
    payment_slip_number = fields.Char(_('Payment Slip Number'))
    error = fields.Text(_('Error'))
    state = fields.Selection([('new', _('New')), ('error', _('Error'))],
                             string='State', default='new')

    @api.multi
    def check_invoices(self):
        res = {}
        inv_obj = self.env['account.invoice']
        for row in self:
            ctx = {}
            file_ext = row.csv_name.split('.')
            if len(file_ext) > 1 and file_ext[1] not in [u'csv', u'CSV']:
                raise UserError(_('The file to import is not CSV'))
            elif len(file_ext) == 1:
                raise UserError(_('The file to import does not have a valid extention'))
            data = base64.b64decode(row.csv_file)
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader_info = []
            if row.delimiter:
                delimiter = str(row.delimiter)
            else:
                delimiter = ','
            reader = csv.reader(file_input, delimiter=delimiter,
                                lineterminator='\r\n')
            try:
                reader_info.extend(reader)
            except Exception:
                raise Warning(_("Not a valid file!"))
            keys = reader_info[0]
            # check if keys exist
            not_found = [x for x in ['reference', 'amount'] if x not in keys]
            if not_found:
                raise Warning(_('The file to be imported does not present the following columns: {}'.format(
                    ', '.join(map(str, not_found)))))
            del reader_info[0]
            active_ids = []
            invoices = {}
            no_doc = ''
            for i in reader_info:
                try:
                    number = str(int(i[0].split('-')[2]))
                except ValueError:
                    number = str(i[0].split('-')[2])
                if not number.isdigit():
                    number = str(int(re.findall('\d+', number)[0]))
                inv_id = inv_obj.search([('secuencial', 'like', number),
                                         ('state', '=', 'open'),
                                         ('partner_id', '=', row.partner_id.id)])
                if inv_id:
                    active_ids.append(inv_id.id)
                    invoices.update({inv_id.id: abs(float(i[1]))})
                else:
                    no_doc += _(
                        'The invoice with the number: {} is not in the system or is in a different state open\n'.format(i[0]))
            ctx.update({'active_ids': active_ids,
                        'active_model': 'account.invoice',
                        'payment_slip_number': row.payment_slip_number,
                        'payment_method_id': row.payment_method_id.id,
                        'batch': True,
                        'invoices': invoices,
                        'errors': no_doc})
            vals_ok = {
                'name': _('Batch Payments from File'),
                'context': ctx,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.register.payments',
                'view_id': False,
                'res_id': False,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
            vals_err = {
                'name': _('Batch Payments from File'),
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.payment.batch.file',
                'view_id': False,
                'res_id': row.id,
                'target': 'new',
                'type': 'ir.actions.act_window',
            }
        if no_doc:
            row.error = no_doc
            row.state = 'error'
            res = vals_err
        else:
            res = vals_ok
        return res


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.model
    def default_get(self, fields):
        context = dict(self.env.context or {})
        active_model = context.get('active_model', False)
        active_ids = context.get('active_ids', False)
        invoices_pay = context.get('invoices', False)
        payment_method_id = context.get('payment_method_id', False)
        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Program error: wizard action executed without"
                              " active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_("Program error: the expected model for this"
                              " action is 'account.invoice'. The provided one"
                              " is '%s'.") % str(active_model))

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open"
                              " invoices"))
        if any(INV_TO_PARTN[inv.type] != INV_TO_PARTN[invoices[0].type]
               for inv in invoices):
            raise UserError(_("You cannot mix customer invoices and vendor"
                              " bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they"
                              " must use the same currency."))
        rec = {}
        if 'batch' in context and context.get('batch'):
            lines = []
            if INV_TO_PARTN[invoices[0].type] == 'customer':
                for inv in invoices:
                    lines.append((0, 0, {'partner_id': inv.partner_id.id,
                                         'invoice_id': inv.id,
                                         'balance_amt': inv.residual or 0.0,
                                         'payment_method_id': payment_method_id or False,
                                         'receiving_amt': invoices_pay[str(inv.id)] if invoices_pay else 0.0,
                                         'payment_difference': abs(inv.residual - invoices_pay[str(inv.id)] if invoices_pay else 0.0) or 0.0,  # noqa
                                         'handling': 'open'
                                         }))
                rec.update({'invoice_customer_payments': lines,
                            'is_customer': True})
            else:
                for inv in invoices:
                    lines.append((0, 0, {'partner_id': inv.partner_id.id,
                                         'invoice_id': inv.id,
                                         'balance_amt': inv.residual or 0.0,
                                         'paying_amt': 0.0}))
                rec.update({'invoice_payments': lines, 'is_customer': False})
        else:
            # Checks on received invoice records
            if any(INV_TO_PARTN[inv.type] != INV_TO_PARTN[invoices[0].type]
                   for inv in invoices):
                raise UserError(_("You cannot mix customer invoices and vendor"
                                  " bills in a single payment."))

        total_amount = sum(inv.residual *
                           INV_TO_PAYM_SIGN[inv.type]
                           for inv in invoices)
        rec.update({
            'payment_slip_number': context.get('payment_slip_number', False),
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': INV_TO_PARTN[invoices[0].type],
        })
        return rec
