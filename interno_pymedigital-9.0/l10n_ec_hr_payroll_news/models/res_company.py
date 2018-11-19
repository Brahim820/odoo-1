#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    loan_account_id = fields.Many2one(
        'account.account', string=_('Loan Account'),
        required=False, )
