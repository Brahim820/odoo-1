# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import re

class AccountAccount(models.Model):
    _inherit = "account.account"

    @api.multi
    @api.onchange('code')
    def _onchange_code(self):
        for r in self:
            if not self.code:
                return
            code = self.code
            self.code = ''.join(re.findall('\d+', code))

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for account in self:

            name = u""
            code = list(account.code)
            structure = account.company_id.account_code_structure.split('.')
            for s in structure:
                if not code:
                    continue

                for i in range(0,int(s)):
                    if code:
                        name += code.pop(0)
                name += '.'

            name = name[:-1] + ' ' + account.name
            result.append((account.id, name))
        return result

