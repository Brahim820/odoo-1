# -*- coding: utf-8 -*-

from openerp import fields, models,tools,api


class pos_config(models.Model):
    _inherit = 'pos.config' 

    pos_kitchen_view = fields.Boolean("Kitchen View",default=False)

