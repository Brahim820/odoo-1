# -*- coding: utf-8 -*-
from openerp import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    account_sueldos_id = fields.Many2one('account.account', string='Cuenta de sueldos por pagar')
