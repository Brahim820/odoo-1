# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.exceptions import UserError
from openerp.tools.translate import _


class purchase_requisition(osv.osv):
    _inherit = 'purchase.requisition'

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Vendor
        """
        context = dict(context or {})
        assert partner_id, 'Vendor should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if not requisition.multiple_rfq_per_supplier and supplier.id in filter(lambda x: x, [
                                        rfq.state != 'cancel' and rfq.partner_id.id or None for rfq in
                                        requisition.purchase_ids]):
                raise UserError(_(
                    'You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % requisition.state)
            context.update({'mail_create_nolog': True})
            purchase_id = purchase_order.create(cr, uid, self._prepare_purchase_order(
                cr, uid, requisition, supplier, context=context), context=context)
            purchase_order.message_post(cr, uid, [purchase_id], body=_("RFQ created"), context=context)
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                seller = line.product_id.seller_ids
                seller = seller.filtered(lambda r: r.name == supplier)
                if seller:
                    purchase_order_line.create(
                        cr, uid, self._prepare_purchase_order_line(
                            cr, uid, requisition, line, purchase_id,
                            supplier, context=context), context=context)
        return res
