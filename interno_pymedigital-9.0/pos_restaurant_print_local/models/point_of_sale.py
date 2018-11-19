# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    order_print_local = fields.Boolean(string='Impresión local',help='Impresión de Ordenes Local', )
