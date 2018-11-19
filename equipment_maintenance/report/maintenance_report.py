# -*- coding: utf-8 -*-

from openerp import tools
from openerp import fields, models


class MaintenanceReport(models.Model):
    _name = "maintenance.report"
    _description = "Maintenance Requests Statistics"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    name = fields.Char('Request Reference', readonly=True)
    date = fields.Datetime('Request Date', readonly=True)
    close_date = fields.Datetime('Close Date', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Sender', readonly=True)
    user_id = fields.Many2one('res.users', 'Repair Responsible', readonly=True)
    picking_type_id = fields.Many2one("stock.picking.type", "Picking Type", readonly=True)
    picking_id = fields.Many2one("stock.picking", "Picking", readonly=True)
    team_id = fields.Many2one('maintenance.team', 'Maintenance Team', readonly=True)
    nbr = fields.Integer('# of Lines', readonly=True)
    stage_id = fields.Many2one('hr.equipment.stage', string='Stage', readonly=True)
    equipment_id = fields.Many2one('hr.equipment', 'Equipment', readonly=True)
    categ_id = fields.Many2one('hr.equipment.category', 'Equipment Category', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    qty = fields.Integer("Used part(qty)", readonly=True)
    note = fields.Text("Note",readonly=True)

    def _select(self):
        select_str = """
            SELECT er.id as id,
                    er.name as name,
                    er.equipment_id as equipment_id,
                    pr.product_id as product_id,
                    sum(pr.qty) as qty,
                    count(*) as nbr,
                    er.stage_id as stage_id,
                    er.request_date as date,
                    er.close_date as close_date,
                    er.employee_id as employee_id,
                    er.picking_type as picking_type_id,
                    er.picking_id as picking_id,
                    er.user_id as user_id,
                    er.category_id as categ_id,
                    er.team_id as team_id,
                    er.description as note        
            """
        
        return select_str

    def _from(self):
        from_str = """
                hr_equipment_request er                
                    left join product_request pr on (pr.equipment_request_id = er.id)
                    join hr_equipment e on (er.equipment_id = e.id)
                    join hr_equipment_stage s on (er.stage_id = s.id)
                    join hr_employee emp on er.employee_id = emp.id
                    left join product_product p on (pr.product_id=p.id)
                    """
        return from_str
    
    def _group_by(self):
        group_by_str = """
                group by pr.product_id,
                    er.id,
                    pr.equipment_request_id,
                    er.team_id,
                    er.equipment_id,
                    er.request_date,
                    er.close_date,
                    er.employee_id,
                    er.picking_type,
                    er.stage_id,
                    er.picking_id,
                    er.user_id,
                    er.category_id,
                    er.name,
                    er.description
                    """
        return group_by_str

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM ( %s )
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
