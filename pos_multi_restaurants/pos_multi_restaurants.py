# -*- coding: utf-8 -*-


from openerp import fields, models,tools,api
import logging
_logger = logging.getLogger(__name__)

class pos_multi_restaurants(models.Model):
    _name = 'pos.multi.restaurants'

    name = fields.Char('Name')
    image = fields.Binary('Image')
    restaurant_manager = fields.Many2one("res.partner")
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    website = fields.Char('Website')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State')
    country_id = fields.Many2one('res.country', 'Country')
    email = fields.Char('Email')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    mobile = fields.Char('Mobile')
    description = fields.Text("Description")
    rest_product_ids = fields.Many2many(comodel_name='product.product',relation='multirestaurants_product',column1='restaurant_id',column2='product_id')
    floor_id = fields.One2many('restaurant.floor','pos_restaurant_id')

class product_product(models.Model):
    _inherit = 'product.product'

    wv_restaurant_id = fields.Many2many(comodel_name='pos.multi.restaurants',relation='multirestaurants_product',column1='product_id',column2='restaurant_id', string="Restaurant")

class pos_config(models.Model):
    _inherit = 'pos.config' 
    
    pos_multi_restaurant = fields.Many2one('pos.multi.restaurants','Restaurant')

class restaurant_floor(models.Model):
    _inherit = 'restaurant.floor' 
    
    pos_restaurant_id = fields.Many2one('pos.multi.restaurants','Restaurant')
    