# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields


class AccountMoveLineReport(models.Model):
    _name = "account.move.line.report"
    _description = "Move line reports"
    _auto = False
    _rec_name = 'date'

    date = fields.Date('Fecha', readonly=True)
    name = fields.Char(string='Nombre', size=128)
    ref = fields.Char(string='Referencia', size=128)
    move_id = fields.Many2one('account.move', 'Movimiento')
    journal_id = fields.Many2one('account.journal', 'Diario')
    account_id = fields.Many2one('account.account', 'Cuenta')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica')
    reconciled = fields.Boolean('Conciliado')
    partner_id = fields.Many2one('res.partner', 'Empresa')
    credit = fields.Float(string="Crédito")
    debit = fields.Float(string="Débito")

    _order = 'date desc'

    _depends = {
        'account.move.line': [
            'reconciled', 'credit', 'debit'
        ],
        'account.move': [
            'date'
        ],
    }

    @staticmethod
    def _query():
        query_str = """

select ml.id, ml.name, ml.ref, m.date, m.id as move_id, aj.id as journal_id, aa.id as account_id, ml.analytic_account_id, ml.reconciled,
  ml.partner_id, ml.credit, ml.debit
FROM account_move m, account_move_line ml, account_journal aj, account_account aa
where m.id = ml.move_id and m.journal_id = aj.id AND aa.id = ml.account_id

        """
        return query_str

    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            )""" % (
                    self._table, self._query()
                    )
                   )
