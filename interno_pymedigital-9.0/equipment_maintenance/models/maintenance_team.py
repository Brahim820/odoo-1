# -*- coding: utf-8 -*-

from openerp import api, fields, models


class MaintenanceTeam(models.Model):
    _name = "maintenance.team"

    name = fields.Char(required=True)
    leader_id = fields.Many2one('res.users', string='Leader', required=True)
    member_ids = fields.One2many("res.users", 'maintenance_team_id', string='Team Members')
    location_id = fields.Many2one("stock.location", string="Preferred Location")


class ResUsers(models.Model):
    _inherit = 'res.users'

    maintenance_team_id = fields.Many2one('maintenance.team', string='Maintenance Team')
