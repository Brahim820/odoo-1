# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class AccountAccount(models.Model):
    _inherit = "account.account"

    legacy_code = fields.Char(string='Legacy code', )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(
            [
                '|','|',
                ('legacy_code', operator, name),
                ('name', operator, name),
                ('code', operator, name)
            ] + args, limit=limit)
        return recs.name_get()
