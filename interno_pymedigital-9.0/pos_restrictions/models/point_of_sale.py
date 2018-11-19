# -*- coding: utf-8 -*-

from openerp import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    user_ids = fields.Many2many(
        'res.users', 'pos_config_users_rel',
        'pos_config_ids', 'user_ids', string='Users allowed in this POS', )
