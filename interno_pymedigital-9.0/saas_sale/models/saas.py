# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaasClient(models.Model):
    _inherit = 'saas.client'

    odoodb_id = fields.Many2one('federate.database', string='Odoo Database', )
