# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pos_config(models.Model):
	_inherit = 'pos.config'

	is_customer_mandatory = fields.Boolean("Is Customer Mandatory", help='An option to mandatory customer selection before payment in POS session')
