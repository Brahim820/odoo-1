from openerp import fields, api, models, _

class pos_order(models.Model):

    _inherit = "pos.order"

    pricelist_id = fields.Many2one('product.pricelist', 'PriceList')

    @api.model
    def _order_fields(self, ui_order):
        res = super(pos_order, self)._order_fields(ui_order)
        if ui_order.has_key('pricelist_id') and ui_order.get('pricelist_id'):
            res.update({
                'pricelist_id': ui_order.get('pricelist_id')
            })
        return res