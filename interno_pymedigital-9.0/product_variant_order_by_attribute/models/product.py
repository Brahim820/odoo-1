# -*- coding: utf-8 -*-
from openerp import models, fields


class PosOrder(models.Model):
    _inherit = 'product.attribute.value'
    _order = 'attribute_id'
    
    # Changes the default order to attribute_id instead of sequence
