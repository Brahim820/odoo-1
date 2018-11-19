# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import _, api, fields, models


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def get_last_opening_balance(self):
        last_bnk_stmt = self.search(
            [('journal_id', '=', self.journal_id.id), ('date', '<', self.date)], limit=1)
        if last_bnk_stmt:
            self.balance_start = last_bnk_stmt.balance_end

    @api.multi
    def _check_first_statement(self):
        for row in self:
            res = False
            if row.state == 'open':
                statements = self.search(
                    [('journal_id', '=', row.journal_id.id), ('date', '<', row.date)])
                if len(statements) == 0:
                    res = True
            row.first_statement = res

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        res = super(AccountBankStatement, self).onchange_journal_id()
        statements = self.search(
            [('journal_id', '=', self.journal_id.id), ('date', '<', self.date)])
        if len(statements) == 0:
            self.first_statement = True
        return res

    first_statement = fields.Boolean(
        _('First Statement'), compute=_check_first_statement)


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    source_move_line_id = fields.Many2one(
        'account.move.line', string="Source move line", )
