# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    session_format_id = fields.Many2one('report.custom.format', string=u"Formato de reporte de sesión", )

