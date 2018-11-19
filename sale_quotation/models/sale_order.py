# -*- coding: utf-8 -*-
####################################################
# Parte del Proyecto LibreGOB: http://libregob.org #
# Licencia AGPL-v3                                 #
####################################################

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_line_ids = fields.One2many(
        'sale.quotation.line',
        'order_id',
        string='Quotation lines',
         )


class SaleQuotationLine(models.Model):
    _name = 'sale.quotation.line'
    _description = 'Sale Quotation Line'

    name = fields.Char(string='Name', )
    description = fields.Text(string='Description', )
    order_id = fields.Many2one('sale.order', string='Order', )
    category_id = fields.Many2one('sale.quotation.category', string='Category', )


class SaleQuotationCategory(models.Model):
    _name = 'sale.quotation.category'
    _description = 'Sale Quotation Category'

    name = fields.Char(string="name", )
    description = fields.Text(string='Description', )
    image = fields.Binary(string='Image', attachment=True, )


