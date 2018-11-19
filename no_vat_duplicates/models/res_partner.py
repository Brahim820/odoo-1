# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.constrains('vat', 'parent_id', 'company_id')
    def _check_vat_duplicates(self):
        for r in self:
            r.no_vat_duplicates()

    @api.multi
    def no_vat_duplicates(self):
        """
        Checks if several partners have the same VAT.
        Only allows duplication if the partners are related
        on a parent-child relationship.
        """
        if not self.vat:
            return

        partner_obj = self.env['res.partner']
        partners = partner_obj.search([
            ('vat', '=', self.vat),
            ('company_id', '=', self.company_id.id),
        ])

        partners -= partners.mapped('child_ids')

        if len(partners) > 1:
            raise UserError(
                _("You have more than one partner with the same VAT: %s  \
                  If the new partner is related, like a contact, set the  \
                  company in order to allow the same VAT on main partner \
                  and it's childs. "
                ) % (', '.join(partners.mapped('name')))
            )

        return True

