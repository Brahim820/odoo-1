# -*- coding: utf-8 -*-


# import logging

# import openerp

# from openerp import tools
# from openerp.osv import fields, osv
# from openerp.tools.translate import _

# class pos_config(osv.osv):
#     _inherit = 'pos.config' 
#     _columns = {
#         'allow_lock': fields.boolean('Allow Screen Lock'),
#     }

from openerp import fields, models,tools

class pos_multi_store(models.Model):
    _name = 'pos.multi.store'

    name = fields.Char('Name')
    image = fields.Binary('Image')
    store_manager = fields.Many2one("res.partner")
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
    product_id = fields.Many2many('product.product', 'Product')