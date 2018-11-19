# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import traceback

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_check_partner_stock(self):
        database = self.partner_id.database_ids \
            or self.partner_id.parent_id.database_ids

        if not database:
            raise UserError(_('No database information in partner.'))

        try:
            odoo = database[0].connect_odoorpc()

            product_obj = odoo.env['product.product']
            wh_obj = odoo.env['stock.warehouse']
            quant_obj = odoo.env['stock.quant']

            wh_name = self.partner_id.name
            wh = wh_obj.browse(wh_obj.search([('name', '=', wh_name)]))
            loc = wh.lot_stock_id.id
            for line in self.move_lines_related:
                product_id = line.product_id
                product = product_obj.search([('default_code', '=', product_id.default_code)], limit=1)

                if not product:
                    continue
                partner_product = product_obj.browse(product)

                quant_data = quant_obj.search([
                    ('product_id', '=', partner_product.id),
                    ('location_id', '=', loc ),
                    ('reservation_id', '=' , False)
                ])
                quant_ids = quant_obj.browse(quant_data)
                available = sum([x.qty for x in quant_ids]) if len(quant_ids) > 0 else 0.00

                line.write({'partner_stock': available })

        except:
            _logger.warning(
                'Fail to create sale order with error: %s' % traceback.print_exc())

        database.disconnect_odoorpc(odoo)


class StockMove(models.Model):
    _inherit = 'stock.move'

    partner_stock = fields.Float(string='Partner stock', )

