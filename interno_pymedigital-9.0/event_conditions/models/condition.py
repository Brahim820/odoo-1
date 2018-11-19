# -*- coding: utf-8 -*-
from openerp import models, fields


class EventCondition(models.Model):
    _name = 'event.condition'

    name = fields.Char("Condition", )
    description = fields.Char("Description", )
    highlight = fields.Boolean(string='Highlight', )
    event_ids = fields.Many2many(
        'event.event', 'event_condition_rel', 'event_ids',
        'condition_ids', string="Events", )
