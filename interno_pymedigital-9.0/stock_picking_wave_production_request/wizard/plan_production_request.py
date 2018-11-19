#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import re
import StringIO
from datetime import datetime, timedelta

import pandas as pd
import xlrd
import xlsxwriter
from openerp import _, api, fields, models
from openerp.exceptions import UserError


class PlanProductionRequest(models.TransientModel):
    """
    Generate and Imports Plan Production Request from File
    """
    _name = 'plan.production.request'
    _description = __doc__

    name = fields.Char(_('Name'))
    file_template = fields.Binary(_('Template'))
    file_upload = fields.Binary(_('Template'))
    date_from = fields.Date(_('Date From'), default=fields.Datetime.now())
    date_to = fields.Date(_('Date To'))
    option = fields.Selection([('export', _('Export Template')),
                               ('import', _('Import Template'))], string=_('Option'), default='export')
    wave_id = fields.Many2one('stock.picking.wave', string=_(
        'Wave'), default=lambda x: x.env.context.get('active_id'))
    state = fields.Selection([('draft', _('Draft')),
                              ('exported', _('Exported'))], string='State', default='draft')

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from:
            date_from = datetime.strptime(self.date_from, '%Y-%m-%d')
            self.date_to = date_from + timedelta(days=6)

    def daterange(self, date_from, date_to):
        for date_step in range(int((date_to - date_from).days)):
            yield date_from + timedelta(date_step)

    @api.multi
    def generate_template(self):
        file_data = StringIO.StringIO()
        xbook = xlsxwriter.Workbook(file_data, {'in_memory': True})
        xsheet = xbook.add_worksheet(self.wave_id.name.replace('/', '_'))
        date_range = []
        date_from = datetime.strptime(self.date_from, '%Y-%m-%d')
        date_to = datetime.strptime(self.date_to, '%Y-%m-%d')
        for single_date in self.daterange(date_from, date_to + timedelta(days=1)):
            if single_date.weekday() != 6:
                date_range.append(single_date.strftime("%Y-%m-%d"))
        header = [_('ID'), _('Manofacturing Request'), _(
            'Date Planned'), _('Product'), _('Quantity'), _('UoM')] + date_range
        mr_data = []
        decimal = xbook.add_format({'num_format': '0.00'})
        for w in self.wave_id.mapped('procurement_production_request_ids'):
            data = []
            data.insert(0, w.id or '')
            data.insert(1, w.name or '')
            data.insert(2, w.date_planned)
            data.insert(4, w.product_id.name_get()[0][1])
            data.insert(5, w.product_qty)
            data.insert(6, w.product_uom.name)
            xsheet.write_row(0, 0, header)
            if w.state == 'to_approve':
                mr_data.append(data + [None for x in date_range])
        for line in range(0, len(mr_data)):
            xsheet.write_row(line + 1, 0, mr_data[line])
        xsheet.set_column('A:A', None, None, {'hidden': True})
        xsheet.set_column('B:F', 15)
        xsheet.set_column('E:E', 15, decimal)
        xsheet.set_column('G:Z', 10, decimal)
        xbook.close()
        out = base64.encodestring(file_data.getvalue())
        self.write({'name': _('Plan Production Request: From %s, to %s.xlsx') % (self.date_from, self.date_to),
                    'file_template': out, 'state': 'exported'})
        return {
            'name': _('Plan Production Request'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'plan.production.request',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def import_template(self):
        mr_obj = self.env['mrp.production.request']
        mo_obj = self.env['mrp.production']
        for row in self:
            if not row.file_upload:
                raise UserError(_('Please Select file to import'))
            xdata = base64.b64decode(row.file_upload)
            xbook = xlrd.open_workbook(file_contents=xdata)
            df = pd.read_excel(xbook, self.wave_id.name.replace('/', '_'), engine="xlrd")
            mo_data = {}
            if mo_obj.search([('mrp_production_request_id', 'in', df.ix[:, 0].tolist())]):
                raise UserError(_('The planning file has already been imported!'))
            for index, y in df.iterrows():
                mr_data = mr_obj.browse(y[0])
                data = y.to_dict()
                plan = {}
                if not mo_data or not mo_data.get(mr_data.id):
                    mo_data.update({
                        mr_data.id: []
                    })
                for mr in data:
                    if re.match(r"^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])|.([0-9])$", mr):
                        plan[mr] = data[mr]
                for pl in plan:
                    if type(plan[pl]) in [int, float] and plan[pl] > 0:
                        mo_data[mr_data.id].append({
                            'product_id': mr_data.product_id.id,
                            'product_qty': plan[pl],
                            'product_uom': mr_data.product_uom.id,
                            'date_planned': pl.split('.')[0],
                            'bom_id': mr_data.bom_id and mr_data.bom_id.id or False,
                            'location_src_id': mr_data.location_src_id.id,
                            'location_dest_id': mr_data.location_dest_id.id,
                            'mrp_production_request_id': mr_data.id,
                            'wave_id': mr_data.wave_id.id
                        })
            if mo_data:
                for mr, mos in mo_data.iteritems():
                    for mo in mos:
                        mo_obj.create(mo)
                row.wave_id.procurement_production_request_ids.filtered(
                    lambda x: x.state == 'to_approve').button_approved()
                row.wave_id.procurement_production_ids.filtered(
                    lambda x: x.state == 'draft').signal_workflow('button_confirm')
        return {'type': 'ir.actions.act_window_close'}
