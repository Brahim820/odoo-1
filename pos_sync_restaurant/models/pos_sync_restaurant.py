# -*- coding: utf-8 -*-

from openerp import fields, models,tools,api


class pos_config(models.Model):
    _inherit = 'pos.config' 

    floor_ids = fields.Many2many(comodel_name='restaurant.floor',relation='restaurant_floor_config',column1='restaurant_floor_id',column2='config_id')

class restaurant_floor(models.Model):
    _inherit = 'restaurant.floor' 
    
    pos_config_id = fields.Many2many(comodel_name='pos.config',relation='restaurant_floor_config',column1='config_id',column2='restaurant_floor_id')

