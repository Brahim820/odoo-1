# -*- coding: utf-8 -*-

from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_config_ids = fields.Many2many(
        'pos.config', 'pos_config_users_rel',
        'user_ids', 'pos_config_ids', string='Allowed Point of sales', )
