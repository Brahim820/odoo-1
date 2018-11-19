# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    inventory_voucher_format_id = fields.Many2one('report.custom.format', string="Inventory", )
    stock_move_voucher_format_id = fields.Many2one('report.custom.format', string="Stock Move", )

