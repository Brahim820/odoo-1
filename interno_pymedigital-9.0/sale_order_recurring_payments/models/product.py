# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    recurring = fields.Boolean("Recurring payment", )
    in_advance = fields.Boolean(
        "In advance", help="If selected, payment will be charged in advance.")
    frequency = fields.Integer(
        'Frequency of collection', default=30,
        help='Frecuency in days, Ejem: 30 for a monthy payment', )
