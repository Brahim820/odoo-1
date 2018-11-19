# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp.osv import fields, osv

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        
        'pos_categ_id': fields.many2many('pos.category',  'pos_template', 'pos_category_id', 'tempcat',string='Point of Sale Categories'),
    }