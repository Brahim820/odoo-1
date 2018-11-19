from openerp import _, api, fields, models


class ResPartner(models.Model):
    """
    International Partner
    """
    _inherit = 'res.partner'

    @api.one
    @api.depends('country_id', 'company_id.country_id')
    def _is_international(self):
        company_country = self.company_id.country_id.id
        partner_country = self.country_id.id
        if partner_country:
            if company_country != partner_country:
                self.is_international = True

    is_international = fields.Boolean(_('International partner'),
                                      compute=_is_international,
                                      default=False, store=True)
