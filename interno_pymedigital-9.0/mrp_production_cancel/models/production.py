# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def action_cancel(self):
        res = super(MrpProduction, self).action_cancel()
        if not res:
            return

        for p in self:
            if any(m.state == 'done' for m in p.move_created_ids2):
                p.write({'state':'done'})
        return res

    @api.multi
    def unlink(self):
        raise UserError(_("You cannot delete productions."))

