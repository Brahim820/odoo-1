# -*- coding: utf-8 -*-
from openerp import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    cancel_reason_id = fields.Many2one(
        'mrp.production.cancel.reason',
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict")


class MrpProductionCancelReason(models.Model):
    _name = 'mrp.production.cancel.reason'
    _description = 'Mrp Production Cancel Reason'

    name = fields.Char('Reason', required=True, translate=True)
    active = fields.Boolean(
        'Active', default=True,
        help="By unchecking the active field, you may hide the record \
        you will not use.")

