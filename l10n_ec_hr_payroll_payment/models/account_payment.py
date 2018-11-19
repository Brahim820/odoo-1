# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('prepayment')
    def _onchange_prepayment(self):
        if not self.prepayment and not self.payroll_slip_id:
            self.contrapartida_id = False

    payroll_slip_id = fields.Many2one('hr.payslip')
    payroll_slip_run_id = fields.Many2one('hr.payslip.run')
