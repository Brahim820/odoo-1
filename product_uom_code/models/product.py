# -*- coding: utf-8 -*-
from openerp import fields, models


class ProductUom(models.Model):
    _inherit = 'product.uom'

    code = fields.Char('Code', )
