# -*- coding: utf-8 -*-
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pos_color = fields.Selection([
        ('default', 'Default (green)'),
        ('red', 'Red'),
        ('blue', 'Blue'),
    ], string="POS Color", default='default')
