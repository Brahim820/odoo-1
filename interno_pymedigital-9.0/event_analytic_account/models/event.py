# -*- encoding: utf-8 -*-
from openerp import api, fields, models


class Event(models.Model):
    _inherit = 'event.event'

    project_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account', copy=False, domain=[('account_type', '=', 'normal')],
        help="The analytic account related to this event.", )