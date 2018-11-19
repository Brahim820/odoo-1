# -*- coding: utf-8 -*-
from openerp import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    default_format_id = fields.Many2one('report.custom.format', string="Default Format for reports", )

