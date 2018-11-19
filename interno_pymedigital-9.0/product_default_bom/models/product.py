# -*- coding: utf-8 -*-

import logging

from openerp import fields, models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_bom_id = fields.Many2one(
        'mrp.bom',
        domain="[('product_id','=', id)]",
        string='Default bom', )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    default_bom_id = fields.Many2one(
        'mrp.bom',
        domain="[('product_tmpl_id','=', id)]",
        string='Default bom', )

