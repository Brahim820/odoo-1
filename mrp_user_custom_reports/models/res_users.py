# -*- coding: utf-8 -*-
from openerp import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    production_format_id = fields.Many2one('report.custom.format', string="Production Report Format", )
