# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, _
from openerp import exceptions
from datetime import datetime


class AccountInvoiceSession(models.Model):
    _inherit = 'account.invoicing.session'

    payment_ids = fields.Many2many(
        'account.payment', 'payment_session_rel', 'payment_ids',
        'invoicing_session_ids', string="Payments", )

    summary_ids = fields.One2many(
        'account.payment.summary', inverse_name='invoicing_session_id',
        ondelete='restrict', string="Payment sumary", )

    @api.multi
    def button_session_closed(self):
        super(AccountInvoiceSession, self).button_session_closed()
        for s in self:
            s.get_account_payment_summary()

    @api.multi
    def get_account_payment_summary(self):
        for s in self:
            s.summary_ids.unlink()
            summaries = {}
            for p in s.payment_ids:

                inbound = 0.0
                outbound = 0.0
                if p.payment_type == 'inbound':
                    inbound = p.amount
                elif p.payment_type in ('outbound','transfer'):
                    outbound = p.amount

                j_val = {
                    'invoicing_session_ids': s.id,
                    'journal_id': p.journal_id.id,
                    'outbound': outbound,
                    'inbound': inbound,
                }

                key = str(p.journal_id.id)

                if key not in summaries:
                    summaries[key] = j_val
                else:
                    summaries[key]['inbound'] += j_val['inbound']
                    summaries[key]['outbound'] += j_val['outbound']

                if p.payment_type == 'transfer':
                    key = str(p.destination_journal_id.id)

                    d_val = {
                        'invoicing_session_ids': s.id,
                        'journal_id': p.destination_journal_id.id,
                        'outbound': 0.0,
                        'inbound': p.amount,
                    }

                    if key not in summaries:
                        summaries[key] = d_val
                    else:
                        summaries[key]['inbound'] += d_val['inbound']

            for summary in summaries.values():
                print 'summary', summary
                self.env['account.payment.summary'].create(summary)

