# -*- coding: utf-8 -*-
from openerp import fields, models, api, _, registry

import logging

_logger = logging.getLogger(__name__)

class pos_sale_pricelist(models.TransientModel):

    _name = "pos.sale.pricelist"

    @api.model
    def get_price(self, values):
        _logger.info('checking: %s' % values)
        results = {}
        for val in values :
            product = self.env['product.product'].sudo().browse(int(val['product_id'])).with_context(
                lang=val['lang'] if val.has_key('lang') else None,
                partner=int(val['partner_id']) if val.has_key('partner_id') else None,
                quantity=val['quantity'],
                date_order=fields.Datetime.now(),
                pricelist=val['price_id'],
                uom=val['uom_id'],
            )
            _logger.info('%s - %s' % (product.name, product.price))
            results[product.id] = product.price
        return results