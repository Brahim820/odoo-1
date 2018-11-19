# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError

PRODUCTION_STATES = ['draft', 'confirmed', 'ready', 'in_production']


class MrpProductionCancel(models.TransientModel):

    """ Ask a reason for the mrp.production cancellation."""
    _name = 'mrp.production.cancel'
    _description = __doc__

    reason_id = fields.Many2one(
        'mrp.production.cancel.reason',
        string='Reason',
        required=True)

    @api.multi
    def confirm_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        production_ids = self._context.get('active_ids')
        if production_ids is None:
            return act_close
        assert len(production_ids) == 1, "Only 1 production ID expected"
        production = self.env['mrp.production'].browse(production_ids)
        production.cancel_reason_id = self.reason_id.id
        # in the official addons, they call the action_cancel()
        # but directly call action_cancel on productions orders
        if production.state in PRODUCTION_STATES:
            production.action_cancel()
        else:
            raise UserError(
                _("You cannot cancel the"
                  " Production in the current state!"))
        return act_close

