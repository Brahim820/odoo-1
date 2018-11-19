from openerp.osv import fields, osv


class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'


    def write(self, cr, uid, ids, vals, context=None):
        if 'uom_id' in vals:
#            new_uom = self.pool.get('product.uom').browse(cr, uid, vals['uom_id'], context=context)
#            for product in self.browse(cr, uid, ids, context=context):
#                old_uom = product.uom_id
#                if old_uom != new_uom:
#                    if self.pool.get('stock.move').search(cr, uid, [
#                        ('product_id', 'in', [x.id for x in product.product_variant_ids]), ('state', '=', 'done')], limit=1,
#                                                          context=context):
                #  raise UserError(_(
                #  "You can not change the unit of measure of a product that has already been used in a done stock move. If you need to change the unit of measure, you may deactivate this product."))
            return super(product_template, self).write(cr, uid, ids, vals, context=context)
