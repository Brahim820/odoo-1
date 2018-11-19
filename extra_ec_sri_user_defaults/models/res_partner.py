# -*- coding: utf-8 -*-
from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def default_fiscal_position(self):
        vat = self.vat

        if len(vat) == '10':
            persona = '01'
        elif len(vat) == '13':
            persona = '02'




        fiscal = self.property_account_position_id


