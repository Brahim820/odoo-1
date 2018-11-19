# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    factura_format_id = fields.Many2one('report.custom.format', string="Formato de factura", )
    retencion_format_id = fields.Many2one('report.custom.format', string="Formato de retención", )

