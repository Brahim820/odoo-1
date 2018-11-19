# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, exceptions, _
from datetime import datetime


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            session = self.env['account.invoicing.session'].search([('user_id', '=', self.env.user.id), ('state', '=', 'opened'), ('journal_id', '=', self.journal_id.id)])

            if session:
                self.invoicing_session_ids = session[0]
            else:
                journal = self.journal_id
                if journal.require_invoicing_session and len(session) == 0:
                    journal_type = journal.type
                    if journal_type == 'purchase':
                        action = self.env.ref('account_invoicing_session.purchase_list_action')
                        raise exceptions.RedirectWarning(_('At least one purchase session should be open for this user.'), action.id, _('Go to the sessions menu'))
                    if journal_type == 'sale':
                        action = self.env.ref('account_invoicing_session.sale_list_action')
                        raise exceptions.RedirectWarning(_('At least one sale session should be open for this user.'), action.id, _('Go to the sessions menu'))

    invoicing_session_ids = fields.Many2many(
        'account.invoicing.session', 'invoice_session_rel', 'invoicing_session_ids',
        'invoice_ids', string="Session", )

    @api.multi
    @api.constrains('invoicing_session_ids')
    def _check_invoicing_session_ids(self):
        for r in self:
            if len(r.invoicing_session_ids) > 1:
                raise exceptions.ValidationError(_('The invoice should belong to only one invoicing session'))


class AccountInvoicingSession(models.Model):
    _name = 'account.invoicing.session'

    @api.multi
    def button_session_opened(self):
        for s in self:
            s.state = 'opened'

    @api.multi
    def button_session_closed(self):
        for s in self:
            s.state = 'closed'
            s.get_account_payment_summary()
            s.date_to = fields.Datetime.now()

    @api.multi
    def button_session_cancelled(self):
        for s in self:
            s.state = 'cancelled'
            s.invoice_ids = False

    @api.multi
    def button_session_new(self):
        for s in self:
            s.state = 'new'

    @api.multi
    def button_session_done(self):
        for s in self:
            s.state = 'done'
            s.get_account_payment_summary()

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            if not self.journal_id.invoicing_session_sequence_id:
                raise exceptions.UserError(_('There is no sequence configured for this journal. Add a session name manually'))
            self.name = self.journal_id.invoicing_session_sequence_id._next()

    @api.multi
    def button_get_session_payments(self):
        for s in self:
            invoices = s.invoice_ids
            payments = invoices.mapped('payment_ids')
            s.payment_ids += payments

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
                    'invoicing_session_id': s.id,
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
                        'invoicing_session_id': s.id,
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

    @api.multi
    def compute_amounts(self):
        for s in self:
            invoices = s.invoice_ids.filtered(lambda x: x.state in ('open','paid'))
            inv = invoices.filtered(lambda x: 'invoice' in x.type)
            ref = invoices.filtered(lambda x: 'refund' in x.type)

            invoice_amount = sum(i.amount_total for i in inv)
            refund_amount = sum(r.amount_total for r in ref)

            s.invoice_amount = invoice_amount
            s.refund_amount = refund_amount
            s.session_amount = invoice_amount - refund_amount

    invoice_amount = fields.Float('Invoice amount', compute=compute_amounts, )
    refund_amount = fields.Float('Refund amount', compute=compute_amounts, )
    session_amount = fields.Float('Session amount', compute=compute_amounts, )

    name = fields.Char('Name', required=True, copy=False, )
    communication = fields.Char('Communication', )
    date_from = fields.Datetime('Date from', default=fields.Datetime.now(),)
    date_to = fields.Datetime('Date to', )

    state =  fields.Selection([
        ('new', 'New'),
        ('opened', 'In progress'),
        ('closed', 'Closed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='new')
    journal_id = fields.Many2one(
        'account.journal', string='Journal',
        domain=[('type', 'in', ('sale','purchase'))],
        required=True, )
    user_id = fields.Many2one(
        'res.users', string='User',
        default=lambda self: self.env.user,
        readonly=False, )
    invoice_ids = fields.Many2many(
        'account.invoice', 'invoice_session_rel', 'invoice_ids',
        'invoicing_session_ids', string="Invoices", )

    #Related fields
    type = fields.Selection(string='Type',
                            store=True,
                            related='journal_id.type',
                            readonly=True, )

    payment_ids = fields.Many2many(
        'account.payment', 'payment_session_rel', 'payment_ids',
        'invoicing_session_ids', string="Payments", )

    summary_ids = fields.One2many(
        'account.payment.summary', inverse_name='invoicing_session_id',
        ondelete='restrict', string="Payment sumary", )
