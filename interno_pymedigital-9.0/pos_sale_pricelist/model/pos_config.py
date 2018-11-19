from openerp import fields, api, models, _

class pos_config(models.Model):

    _inherit = "pos.config"

    multi_pricelist = fields.Boolean('Multi Pricelist')
