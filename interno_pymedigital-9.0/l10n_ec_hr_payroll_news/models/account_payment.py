#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    loan_id = fields.Many2one('hr.payslip.loans', string=_('Loan'),)
