# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    saas_client_id = fields.Many2one('saas.client', string="Saas Client", )
