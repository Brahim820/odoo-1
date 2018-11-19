from openerp import api, fields, models, _

class res_partner(models.Model):
    _inherit = "res.partner"

    pos_pricelist_id = fields.Many2one('product.pricelist', 'POS Price list', related='property_product_pricelist', store=True)


