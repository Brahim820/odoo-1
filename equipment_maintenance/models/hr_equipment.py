# -*- coding: utf-8 -*-

from datetime import date, datetime

from openerp import _, api, fields, models

from dateutil.relativedelta import relativedelta


class ProductCategoryInherited(models.Model):
    _inherit = "product.category"

    # @api.onchange("parent_id", 'parent_id.part')
    # def onchange_parent(self):
    #     if self.parent_id:
    #         self.part = self.parent_id.part

    part = fields.Boolean("Part/Component")


class HrEquipmentInherited(models.Model):
    _inherit = 'hr.equipment'

    account_asset_id = fields.Many2one("account.asset.asset", string="Account Asset")
    resource_id = fields.Many2one("resource.resource", string="Resource")
    # product_id = fields.Many2one("product.template",string="Product")
    category_id = fields.Many2one('hr.equipment.category',
                                  string='Equipment Category', track_visibility='onchange')
    name = fields.Char('Equipment Name', required=True, translate=True)
    team_id = fields.Many2one("maintenance.team", string="Maintenance Team", required=True)
    maintenance_startdate = fields.Date(
        "Maintenace Start Date", default=date.today(), required=True)
    maintenance_enddate = fields.Date("Maintenace End Date")
    maintenance_nextdate = fields.Date(
        "Maintenace Next Date", default=date.today() + relativedelta(months=+1))

    @api.onchange('maintenance_startdate')
    def change_nextdate(self):
        if self.maintenance_startdate:
            self.maintenance_nextdate = datetime.strptime(self.maintenance_startdate, '%Y-%m-%d') + \
                relativedelta(months=+1)

    @api.model
    def add_request(self, ids=None):
        equipments = self.search([])
        for equipment in equipments:
            stage_ids = [x.id for x in self.env['hr.equipment.stage'].search(
                [('done', '=', False)])]
            has_planned = self.env['hr.equipment.request'].search(
                [('equipment_id', '=', equipment.id), ('request_date', '>', date.today().strftime('%Y-%m-%d')),
                 ('stage_id', 'in', stage_ids)])
            if equipment.maintenance_nextdate and not has_planned:
                if equipment.maintenance_nextdate >= date.today().strftime(
                        '%Y-%m-%d') and equipment.maintenance_enddate >= date.today().strftime('%Y-%m-%d'):
                    if equipment.equipment_assign_to == 'employee':
                        m_request_vals = {
                            'name': equipment.name + '-' + equipment.employee_id.name + _('Planned'),
                            'employee_id': equipment.employee_id.id,
                            'equipment_id': equipment.id,
                            'user_id': equipment.user_id.id,
                            'request_date': equipment.maintenance_nextdate,
                            'start_date': equipment.maintenance_nextdate,
                            'close_date': datetime.strptime(equipment.maintenance_nextdate, '%Y-%m-%d') +
                            relativedelta(hours=+1),
                            'type': 'planned',
                        }
                    else:
                        m_request_vals = {
                            'name': equipment.name + '-' + equipment.department_id.name + _('Planned'),
                            'employee_id': self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id,
                            'equipment_id': equipment.id,
                            'user_id': equipment.user_id.id,
                            'request_date': equipment.maintenance_nextdate,
                            'start_date': equipment.maintenance_nextdate,
                            'close_date': datetime.strptime(equipment.maintenance_nextdate, '%Y-%m-%d') +
                            relativedelta(hours=+1),
                            'department_id': equipment.department_id.id or False,
                            'type': 'planned',
                        }
                    ans = self.env['hr.equipment.request'].create(m_request_vals)
                    if ans:
                        equipment.maintenance_nextdate = date.today() + relativedelta(months=+1)
                else:
                    equipment.maintenance_nextdate = date.today() + relativedelta(months=+1)
        return True


class HrEquipmentRequestInherited(models.Model):
    _inherit = 'hr.equipment.request'

    @api.one
    @api.depends('stage_id')
    def change_stage(self):
        self.stage = self.stage_id.sequence

    @api.returns('self')
    def _default_stage(self):
        return self.env['hr.equipment.stage'].search([], limit=1)

    @api.multi
    def archive_equipment_request(self):
        self.write({'stage_id': self.env['hr.equipment.stage'].search(
            [], order="sequence asc", limit=5)[4].id})

    @api.multi
    def reset_equipment_request(self):
        """ Reinsert the equipment request into the maintenance pipe in the first stage"""
        first_stage_obj = self.env['hr.equipment.stage'].search([], order="sequence asc", limit=1)
        self.write({'stage_id': first_stage_obj.id})

    @api.multi
    def do_inprogress(self):
        self.write(
            {'stage_id': self.env['hr.equipment.stage'].search([], order="sequence asc", limit=2)[1].id,
             'start_date': fields.Datetime.now()})

    @api.multi
    def do_repair(self):
        self.write(
            {'stage_id': self.env['hr.equipment.stage'].search([], order="sequence asc", limit=3)[2].id})

    @api.multi
    def do_scrap(self):
        self.write(
            {'stage_id': self.env['hr.equipment.stage'].search([], order="sequence asc", limit=4)[3].id})

    @api.onchange('picking_type')
    def onchange_picking_type(self):
        if self.picking_type:
            self.location_id = self.picking_type.default_location_src_id.id
            self.dest_location_id = self.picking_type.default_location_dest_id.id
        else:
            self.location_id = ''
            self.dest_location_id = ''

    @api.model
    def create(self, vals):
        ans = super(HrEquipmentRequestInherited, self).create(vals)
        recipient_ids = []
        team = self.env['hr.equipment'].browse([vals['equipment_id']]).team_id
        for mem in team.member_ids:
            if mem.partner_id.id != team.leader_id.partner_id.id:
                recipient_ids.append(mem.partner_id.id)

        recipient_ids.append(team.leader_id.partner_id.id)
        thread_pool = self.env['mail.thread']
        thread_pool.message_post(
            subject=_("New Equipment Request"),
            message_type="notification",
            content_subtype="mt_comment",
            partner_ids=recipient_ids,
            body=_("<p>Hello, </p><p>You got a new Equipment Request:</p>"
                   "<ul><li>Name: ") + vals['name'] + _('</li><li>Equipment: ') + self.env['hr.equipment'].browse(
                [vals['equipment_id']]).name + '</li</ul>',
        )
        return ans

    @api.multi
    def create_picking(self):
        if self.picking_type and self.location_id and self.dest_location_id and self.product_ids:
            move_lines = []
            for part in self.product_ids:
                name = part.product_id.name_get()[0][1]
                if part.product_id.description_sale:
                    name += '\n' + part.product_id.description_sale
                new_line_vals = {
                    'product_id': part.product_id.id,
                    'product_uom': part.product_id.uom_id.id,
                    'product_uom_qty': part.qty,
                    'date': self.request_date,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.dest_location_id.id,
                    'procure_method': 'make_to_stock',
                    'company_id': self.env.user.company_id.id,
                    'state': 'draft',
                    'name': name
                }
                line_tup = (0, False, new_line_vals)
                move_lines.append(line_tup)
            new_vals = {
                'company_id': self.env.user.company_id.id,
                'picking_type_id': self.picking_type.id,
                'move_type': 'one',  # goods to be delivered all at once
                'priority': '1',
                'move_lines': move_lines,
                'date': self.request_date,
                'location_id': self.location_id.id,
                'location_dest_id': self.dest_location_id.id,
                'partner_id': self.employee_id.user_id.partner_id.id
            }
            created_picking = self.env['stock.picking'].create(new_vals)
            self.picking_id = created_picking.id
        return True

    @api.onchange("team_id")
    def onchange_team(self):
        self.location_id = self.team_id.location_id.id

    @api.one
    def default_closedate(self):
        start_date = self.request_date or self.start_date
        if start_date:
            self.close_date = start_date + relativedelta(hours=+2)

    stage_id = fields.Many2one('hr.equipment.stage', string='Stage', track_visibility='onchange',
                               default=_default_stage)
    stage = fields.Char(compute=change_stage, string='stage')
    team_id = fields.Many2one('maintenance.team', related="equipment_id.team_id",
                              string="Maintenance Team", store=True)
    part_require = fields.Boolean("Parts Required?")
    picking_type = fields.Many2one("stock.picking.type", string="Picking Type", domain=[
                                   ('code', '=', 'internal')])
    location_id = fields.Many2one('stock.location', 'Source Location')
    dest_location_id = fields.Many2one('stock.location', 'Destination Location')
    picking_id = fields.Many2one("stock.picking", "Picking")
    product_ids = fields.One2many(
        "product.request", 'equipment_request_id', string="Part/Component")
    request_date = fields.Datetime(
        'Request Date', track_visibility='onchange', default=fields.Datetime.now())
    start_date = fields.Datetime('Start date', track_visibility='onchange',
                                 help="Datetime when the maintenance start")
    close_date = fields.Datetime('Close date', default=default_closedate)
    type = fields.Selection([('planned', 'Planned'), ('demand', 'Under demand')],
                            'Maintenance type', default='demand')


class ProductRequest(models.Model):
    _name = "product.request"

    product_id = fields.Many2one('product.product', string="Product", required=True)
    qty = fields.Integer("Quantity", help="Required Quantity of Product", required=True)
    equipment_request_id = fields.Many2one('hr.equipment.request')
