# -*- coding: utf-8 -*-
from openerp import _, api, fields, models
from openerp.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    compensation_ids = fields.One2many(
        'account.move.line', 'compensation_id',
        string='Compensations',
    )

    compensation_account_id = fields.Many2one(
        'account.account', string='Compensation account', store=True,
        compute='_compute_compensation_account', )

    @api.multi
    @api.depends('journal_id')
    def _compute_compensation_account(self):
        for r in self:
            method = r.payment_method_id.code
            if method != 'compensation':
                return
            journal = self.journal_id
            if journal.default_credit_account_id != journal.default_credit_account_id:
                raise UserError(_(
                    "Debit and credit account must be equal for payment compensation"))
            r.compensation_account_id = journal.default_credit_account_id

    @api.multi
    def post(self):
        for rec in self:
            res = super(AccountPayment, self).post()
            moves = rec.compensation_ids
            moves += rec.move_line_ids.filtered(lambda m: m.account_id == rec.compensation_account_id)
            moves.reconcile()
            return res


class AccountRegisterPayments(models.Model):
    _inherit = 'account.register.payments'

    compensation_ids = fields.One2many(
        'account.move.line', 'compensation_id',
        string='Compensations',
        domain=[('reconciled', '=', False),('partner_id','=','partner_id'),('account_id',"=",'destination_account_id')],
    )

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    compensation_id = fields.Many2one('account.payment', string='Compensation', )

