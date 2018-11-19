# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError

import traceback

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def create_supplier_sale_order(self):
        partner = self.partner_id
        database = partner.database_ids or None
        if database:
            try:
                odoo = database[0].connect_odoorpc()

                if 'sale.order' in odoo.env:
                    Order = odoo.env['sale.order']
                    company = self.env.user.company_id.partner_id
                    client = odoo.env['res.partner'].search([('vat', '=', company.vat)], limit=1)
                    delivery = self.picking_type_id.warehouse_id.name

                    if not client:
                        raise UserError(_('No client to create the sale order'))
                    seller_client = odoo.env['res.partner'].browse(client)

                    shipping = seller_client
                    for child in seller_client.child_ids:
                        if child.name == delivery:
                            shipping = child

                    order_lines = []
                    note = ''
                    for line in self.order_line:
                        seller = line.product_id._select_seller(
                            line.product_id,
                            partner_id=partner,
                            quantity=line.product_qty,
                            date=self.date_order and self.date_order[:10],
                            uom_id=line.product_uom)

                        uom = line.product_uom

                        seller_uom = uom.id
                        if uom.code:
                            seller_uom = odoo.env['product.uom'].search([('code', '=', uom.code)], limit=1)
                            seller_uom = odoo.env['product.uom'].browse(seller_uom).id or uom.id

                        default_code = seller.product_code or line.product_id.default_code
                        product = odoo.env['product.product']
                        product = product.search([('default_code', '=', default_code)], limit=1)

                        pricelist = odoo.env.ref('product.list0')
                        if seller_client.property_product_pricelist:
                            pricelist = seller_client.property_product_pricelist.id

                        if product:
                            order_lines.append((0, 0, {
                                'pricelist_id':  pricelist,
                                'payment_term_id': seller_client.property_payment_term_id and seller_client.property_payment_term_id.id or False,
                                'partner_invoice_id': seller_client.id,
                                'product_id': product[0],
                                'name': ' '.join([unicode(line.product_id.name), '(', uom.name, ')']),
                                'product_uom_qty': line.product_qty,
                                'product_uom': seller_uom,
                            }))
                        else:
                            note += (_(' * El cliente desea %s %s del producto %s pero no se encontró un producto con la referencia interna %s')
                                     % (line.product_qty, uom.name, line.product_id.name, default_code))

                    order_id = Order.create({
                        'name': ' '.join([unicode(company.name), unicode(self.name)]),
                        'partner_id': shipping.id,
                        'validity_date': self.date_order[:10],
                        'client_order_ref': self.name,
                        'order_line': order_lines,
                        'note': note
                    })

                    if not order_id:
                        raise UserError(_("No sale order was created on provider's database."))

                    order = Order.browse(order_id)
                    self.write({'partner_ref': order.name })


            except:
                _logger.warning(
                    'Fail to create sale order with error: %s' % traceback.print_exc())

            database.disconnect_odoorpc(odoo)
        else:
            raise UserError(_('No database information in the supplier.'))
