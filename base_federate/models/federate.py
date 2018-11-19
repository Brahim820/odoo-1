# -*- coding: utf-8 -*-
from openerp import models, fields, api
import traceback

import logging
_logger = logging.getLogger(__name__)

try:
    import odoorpc
except ImportError:
    _logger.error("The module odoorpc can't be loaded, try: pip install odoorpc")


class FederateDatabase(models.Model):
    _name = 'federate.database'

    partner_id = fields.Many2one('res.partner', string='Partner', )
    url = fields.Char(
        string='Server URL',
        help='For example: dababaseurl.com',
        old_name='server', )
    port = fields.Char(
        string='Port', default='80',
                       help="You can try: 80, 8069 as they are the most common.",)
    name = fields.Char(string='Database name', )
    user = fields.Char('Default user', )
    password = fields.Char('User password', )
    state = fields.Selection(
        [('success', 'Conection succesful'),
         ('fail', 'Failed to connect'),
         ], )

    @api.multi
    def test_connect_odoorpc(self, username=False, password=False):
        odoo = self.connect_odoorpc(username=username, password=password)
        if odoo:
            self.state = 'success'
            self.disconnect_odoorpc(odoo)

    @api.multi
    def connect_odoorpc(self, username=False, password=False):
        try:
            odoo = odoorpc.ODOO(host=self.url, port=self.port)
            # TODO: pass username parameter.
            user = self.user
            password = password or self.password
            odoo.login(self.name, user, password)
            return odoo
        except:
            self.state = 'fail'
            _logger.warning(
                'Failing to connect to database %s with message: %s'
                % (self.name, traceback.print_exc()))

    @api.multi
    def disconnect_odoorpc(self, odoo):
        try:
            odoo.logout()
        except:
            _logger.warning(
                'Fail to disconnect to database %s with message: %s'
                % (self.name, traceback.print_exc()))
