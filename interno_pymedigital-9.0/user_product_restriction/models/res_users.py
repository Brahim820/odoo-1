# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.one
    def get_products(self):
        product_obj = self.env['product.template']
        product_domain = []
        if self.route_ids and self.categ_ids:
            product_domain.append('|')
        if self.route_ids:
            product_domain.append(('route_ids', 'in', [x.id for x in self.route_ids]))
        if self.categ_ids:
            product_domain.append(('categ_id', 'in', [x.id for x in self.categ_ids]))
        product_ids = product_obj.search(product_domain)
        if product_ids and product_domain:
            ids = [i.id for i in product_obj.search(product_domain)]
        else:
            ids = []
        self.write({'user_product_ids': [(6, 0, ids)]})

    route_ids = fields.Many2many(
        'stock.location.route',
        'route_user_rel',
        'user_id',
        'route_id',
        'Allowed Routes')

    categ_ids = fields.Many2many(
        'product.category',
        'category_user_rel',
        'user_id',
        'categ_id',
        'Allowed Categories')

    user_product_ids = fields.Many2many(
        'product.template',
        'product_user_rel',
        'user_id',
        'product_id',
        'Allowd Products')
