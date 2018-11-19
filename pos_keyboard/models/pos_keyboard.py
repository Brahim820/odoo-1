# -*- coding: utf-8 -*-
import logging
from openerp import models, fields, api, tools

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pos_code = fields.Char(related='product_variant_ids.pos_code', string='POS Code')
    
    _sql_constraints = [
            ('pos_code_uniq', 'unique (pos_code)', "POS code already exists !"),
    ]
    
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        tools.image_resize_images(vals)
        product_template_id = super(ProductTemplate, self).create(cr, uid, vals, context=context)
        related_vals = {}
        if vals.get('pos_code'):
            related_vals['pos_code'] = vals['pos_code']
        if related_vals:
            self.write(cr, uid, product_template_id, related_vals, context=context)
        return product_template_id


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pos_code = fields.Char(string='POS Code')

    _sql_constraints = [
            ('pos_code_uniq', 'unique (pos_code)', "POS code already exists !"),
    ]

