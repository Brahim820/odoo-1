# -*- encoding: utf-8 -*-
from openerp import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    condition_ids = fields.Many2many(
        'event.condition', 'event_condition_rel', 'condition_ids',
        'event_ids', string="Conditions", )
