# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _prepare_statement_line_vals(self, statement):
        vals = super(AccountMoveLine, self)._prepare_statement_line_vals(statement)
        # If not name, use move_id name to improve autoreconcile.
        if vals['name'] in ('?', '/'):
            vals['name'] = self.move_id.name

        if self.matched_credit_ids:
            vals['amount'] = self.debit - sum(self.matched_credit_ids.mapped('amount'))

        elif self.matched_debit_ids:
            vals['amount'] = (self.credit - sum(self.matched_debit_ids.mapped('amount'))) * -1

        vals.update({'source_move_line_id': self.id,})

        return vals

