# -*- coding: utf-8 -*-
from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    database_ids = fields.One2many(
        'federate.database', inverse_name='partner_id',
        ondelete='restrict', string="Databases", )
