from openerp import api, fields, models, _

class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(selection_add=[('pos_category', 'POS Category')])
    pos_categ_id = fields.Many2one('pos.category', 'POS Category')