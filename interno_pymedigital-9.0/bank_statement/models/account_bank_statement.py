# -*- coding: utf-8 -*-
import json
from openerp import models, fields, api
from openerp.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def _get_start_date(self, journal_id):
        last_bnk_stmt = self.search([('journal_id', '=', journal_id), ('state', '=', 'confirm')], limit=1)
        if last_bnk_stmt:
            return last_bnk_stmt.date
        return False

    @api.multi
    def import_statement_elements(self):
        self.line_ids.unlink()
        statement_line_obj = self.env['account.bank.statement.line']
        date = fields.Date.from_string(self.date)
        moves = self.env['account.move.line'].search([
            ('journal_id', '=', self.journal_id.id),
            ('date', '<=', date),
            ('statement_id', '=', False),
            ('account_id', '=', self.journal_id.default_debit_account_id.id)])

        for move in moves:
            record = {
                'statement_id': self.id,
                'date': move.date,
                'ref': move.ref,
                'name': move.name,
                'partner_id': move.partner_id.id,
                'amount': move.balance,
                'check_number': move.payment_id.check_number or move.payment_id.secuencial,
                'payment_ref': move.move_id.name,
            }
            statement_line_obj.create(record)

    @api.one
    @api.depends('bank_balance_statement', 'credit_no_inc_bank_statement', 'debit_no_inc_bank_statement')
    def _end_bank_balance(self):
        self.total_bank_statement = self.bank_balance_statement - self.credit_no_inc_bank_statement + self.debit_no_inc_bank_statement

    @api.one
    @api.depends('balance_end')
    def _end_odoo_balance(self):
        self.odoo_total_bank_statement = self.balance_end

    @api.multi
    def _balance_check(self):
        if self.odoo_total_bank_statement != self.total_bank_statement:
            raise UserError('No puede confirmar un extracto con saldo Conciliado diferente de saldo Odoo')
        if self.odoo_total_bank_statement != self.balance_end_real:
            raise UserError('El Saldo Inicial y saldo en el sistema no concuerdan')
        super(AccountBankStatement, self)._balance_check()

    bank_balance_statement = fields.Monetary('Saldo en libro bancos')
    credit_no_inc_bank_statement = fields.Monetary('(-) Créditos no inc. en estado de cuenta')
    debit_no_inc_bank_statement = fields.Monetary('(+) Débitos no inc. en estado de cuenta')
    total_bank_statement = fields.Monetary('Total Conciliado', compute='_end_bank_balance')
    odoo_total_bank_statement = fields.Monetary('Total en Odoo', compute='_end_odoo_balance',
                                                readonly=True)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.line_ids:
                raise UserError('No se puede eliminar, borre primero las líneas del extracto ')
        super(AccountBankStatement, self).unlink()

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    check_number = fields.Char('Cheque')
    payment_ref = fields.Char('Comprobante')
