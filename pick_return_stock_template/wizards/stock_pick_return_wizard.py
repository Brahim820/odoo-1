# -*- coding: utf-8 -*-
import base64
import cStringIO
import csv

import openerp.addons.decimal_precision as dp
from openerp import _, api, exceptions, fields, models
from openerp.exceptions import UserError


class StockPickReturnWizard(models.TransientModel):
    _name = "stock.pick.return.wizard"
    _inherit = 'pick.return.wizard'
    _description = "Create picking for the MO"

    request_type = fields.Selection([
        ('manual', _('Manual')),
        ('file', _('File')),
        ('template', ('Template'))], string=_('Request From'), default='manual')
    template_id = fields.Many2one(
        'stock.picking.template', 'Picking Template', )
    file_upload = fields.Binary('File')
    delimeter = fields.Char('Delimeter', default=',', help='Default delimeter is ","')
    pick_return_line_ids = fields.One2many(
        'pick.return.wizard.line',
        'stock_wizard_id',
        string='Moves to execute',
        ondelete='cascade',
    )
    allow_negative = fields.Boolean('Allow Negative')

    @api.onchange('type', 'route_id')
    def _onchange_route_id(self):
        if self.route_id:
            loc_dest = self.location_dest_id
            dest, src, trans, out_type, in_type = self._prepare_locations(loc_dest=loc_dest)

            vals = {
                'location_dest_id': dest.id,
                'location_src_id': src.id,
                'location_trans_id': trans.id,
                'out_picking_type_id': out_type.id,
                'in_picking_type_id': in_type.id,
            }
            self.update(vals)

    @api.multi
    def create_move_lines_from_template(self):
        template = self.template_id

        if self.request_type == 'template' and not template:
            raise exceptions.UserError(_('You need a template to '))
        if self.request_type == 'file' and not self.file_upload:
            raise exceptions.UserError(_('You need a file to '))

        lines = []
        if self.request_type == 'template':
            for line in template.template_line_ids:
                lines.append({
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom.id,
                    'product_uom_qty': line.product_uom_qty,
                    'stock_wizard_id': self.id,
                })
        elif self.request_type == 'file':
            data = base64.b64decode(self.file_upload)
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader_info = []
            if self.delimeter:
                delimeter = str(self.delimeter)
            else:
                delimeter = ','
            reader = csv.reader(file_input, delimiter=delimeter,
                                lineterminator='\r\n')
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            keys = reader_info[0]
            # check if keys exist
            if not isinstance(keys, list) or ('code' not in keys or
                                              'quantity' not in keys):
                raise exceptions.Warning(
                    _("Not 'code' or 'quantity' keys found"))
            del reader_info[0]
            for i in range(len(reader_info)):
                vals = {}
                field = reader_info[i]
                values = dict(zip(keys, field))
                product_id = self.env['product.product'].search(
                    [('default_code', '=', values['code'])])
                vals['product_id'] = product_id.id
                vals['product_uom'] = product_id.uom_id.id
                vals['product_uom_qty'] = values['quantity']
                vals['stock_wizard_id'] = self.id,
                lines.append(vals)
        self.create_pick_return_lines(lines=lines)

    @api.multi
    def stock_create_picking(self):
        self.pick_return_line_ids._fnct_line_stock()
        for row in self:
            if any(x.product_uom_qty_residual for x in row.pick_return_line_ids if x.product_uom_qty_residual < 0) and not row.allow_negative:
                raise UserError(_('¡You can not create picking for the location {}, while you have a negative balance!'.format(
                    row.location_src_id.name_get()[0][1])))
        in_picking, out_picking = self.create_picking()
        pickings = in_picking + out_picking

        context = {'tree_view_ref': 'stock.vpicktree', 'form_view_ref': 'stock.view_picking_form'}
        return {
            'name': _('PICKINGS'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in pickings])],
            'context': context,
        }


class PickReturnWizardLine(models.TransientModel):
    _inherit = "pick.return.wizard.line"

    @api.one
    @api.depends(
        'product_uom_qty',
        'product_id',
        'stock_wizard_id.location_src_id')
    def _fnct_line_stock(self):
        quant_obj = self.env['stock.quant']
        product = self.product_id
        quant_data = quant_obj.search([('product_id', '=', product.id),
                                       ('location_id', '=', self.stock_wizard_id.location_src_id.id),
                                       ('reservation_id', '=', False)])
        quant = sum([x.qty for x in quant_data]) if len(quant_data) > 0 else 0.00

        self.product_uom_qty_current = quant
        self.product_uom_qty_residual = quant - self.product_uom_qty

    stock_wizard_id = fields.Many2one('stock.pick.return.wizard', string='Pick return wizard', )
    product_uom_qty_current = fields.Float(compute="_fnct_line_stock", string='Current Stock', digits=dp.get_precision(
        'Product Unit of Measure'), required=True)
    product_uom_qty_residual = fields.Float(compute="_fnct_line_stock", string='Residual Stock', digits=dp.get_precision(
        'Product Unit of Measure'), required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
