# -*- coding: utf-8 -*-
###############################################################################
#
#   @author: Daniel Alejandro Mendieta <damendieta@fslibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
###############################################################################
from openerp import models, fields, api, _


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    check_deposit_journal_id = fields.Many2one(
        'account.journal', string='Deposit journal', domain=[('type', '=', 'bank')],
        required=True, states={'done': [('readonly', '=', True)]}, )
    check_deposit_account_id = fields.Many2one(
        'account.account', related='check_deposit_journal_id.default_credit_account_id',
        string='Deposit credit account', readonly=True, )

    @api.multi
    def _prepare_counterpart_move_lines_vals(
            self, deposit, total_debit, total_amount_currency):
        res = super(AccountCheckDeposit, self)._prepare_counterpart_move_lines_vals(deposit, total_debit, total_amount_currency)
        res.update({'account_id': self.check_deposit_account_id.id })
        return res