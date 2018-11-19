# -*- coding: utf-8 -*-

from openerp import api, fields, models, tools, _

class pos_config(models.Model):
    _inherit = 'pos.config' 

    # allow_multi_receipt = fields.Boolean('Allow Multi Receipt', default=True)
    multi_receipt_count = fields.Integer('Multi Receipt Count', default=1)


