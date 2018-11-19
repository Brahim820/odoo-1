# -*- coding: utf-8 -*-
from openerp import models, fields


class OdooDatabase(models.Model):
    _name = 'odoo.database'
    _inherit = 'federate.database'

    saas_client_id = fields.Many2one('saas.client', string='Saas Client', )
