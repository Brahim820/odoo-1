# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaasClient(models.Model):
    _inherit = 'saas.client'

    odoo_database_ids = fields.One2many('odoo.database', inverse_name="saas_client_id", string='Odoo Databases', )


class OdooDatabase(models.Model):
    _name = 'odoo.database'
    _inherit = ['federate.database','saas.database']

    saas_client_id = fields.Many2one('saas.client', string='Saas Client', )