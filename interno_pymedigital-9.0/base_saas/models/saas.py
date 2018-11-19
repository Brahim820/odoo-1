# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaaSDatabase(models.AbstractModel):
    _name = 'saas.database'

    usage = fields.Selection([
        ('production', 'Production', ),
        ('internal_test', 'Internal test'),
        ('customer_test', 'Customer test'),
        ('hot_backup', 'Hot backup'),
        ('template', 'Template'),
    ], )


class SaasApp(models.Model):
    _name = 'saas.app'

    name = fields.Char('Name', )


class SaasClient(models.Model):
    _name = 'saas.client'

    name = fields.Char('Name', required=True, )
    server_id = fields.Many2one('saas.server', string='Server', )
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('cancel', 'Cancelled'),
    ], default='new', )


class SaasAppVersion(models.Model):
    _name = 'saas.app.version'

    name = fields.Char('Name', )


class SaasService(models.Model):
    _name = 'saas.service'

    name = fields.Char('Name', )
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('deprecated', 'Deprecated'),
    ], default='new', )


class SaasServer(models.Model):
    _name = 'saas.server'

    name = fields.Char('Name', )
    public_ip = fields.Char('Public IP', )
    main_domain = fields.Char('Main Domain', )
    state = fields.Selection([
        ('new', 'New'),
        ('active','Active'),
        ('deprecated', 'Deprecated'),
    ], default='new', )
    client_ids = fields.One2many('saas.client', inverse_name='server_id', )
