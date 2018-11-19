# -*- coding: utf-8 -*-
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    procurement_ok = fields.Boolean('Procurement processed', copy=False)

    # as wave_id is refered to the pickings to supply
    procurement_wave_id = fields.Many2one(
        'stock.picking.wave', 'Picking Wave', copy=False)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    raw_ok = fields.Boolean('Raw OK', )
    semifinished_ok = fields.Boolean('Semi OK', )
    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )


class StockMove(models.Model):
    _inherit = 'stock.move'

    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )


class MakeProcurement(models.Model):
    _inherit = 'make.procurement'

    qty = fields.Float(digits=dp.get_precision('Product Unit of Measure'))

    state = fields.Selection([
        ('new', 'new'),
        ('done', 'done'),
    ], default='new', string='State', )
    wave_id = fields.Many2one('stock.picking.wave', 'Picking Wave', )

    @api.multi
    def make_procurement(self):
        for r in self:
            res = super(MakeProcurement, self).make_procurement()
            if res:
                res = self.env['procurement.order'].browse(res['res_id'])
            wave = r.wave_id.id
            if wave:
                res.write({'wave_id': wave, })
                res.propagate_wave(wave=wave, order=res)
            r.write({'state': 'done', })


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def default_wave_id(self):
        active_model = self._context.get('active_model', False)
        if active_model == 'stock.picking.wave':
            active_id = self._context.get('active_id', False)
            wave = self.env['stock.picking.wave'].browse(active_id)
            return wave

    wave_id = fields.Many2one(
        'stock.picking.wave', 'Picking Wave', default=default_wave_id, )

    @api.multi
    def propagate_wave(self, wave, order):
        if order.production_id:
            order.production_id.write({'wave_id': wave, })
        if order.purchase_id:
            order.purchase_id.write({'wave_id': wave, })
        if order.move_ids:
            # Writes the wave on moves and pickings
            order.move_ids.write({'wave_id': wave, })
            order.move_ids.mapped('picking_id').write(
                {'procurement_wave_id': wave, })

    @api.multi
    def run(self, autocommit=False):
        for r in self:
            res = super(ProcurementOrder, self).run(autocommit=autocommit)
            wave = r.wave_id.id
            if wave:
                r.propagate_wave(wave=wave, order=self)
            return res


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    group_id = fields.Many2one(
        'procurement.group', string="Procurement Group",
        copy=False, )

    procurement_ids = fields.One2many('procurement.order', 'wave_id', string='Procurements', )
    make_procurement_ids = fields.One2many(
        'make.procurement', 'wave_id', string='Make Procurement', )

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True, )
    date_planned = fields.Datetime('Date planned', default=lambda self: fields.datetime.now(), )
    user_id = fields.Many2one(default=lambda self: self.env.user, )

    # TODO: delete after migration.
    production_file = fields.Binary('Production', attachment=True, readonly=True, )
    production_filename = fields.Char(string="Production filename", )
    # TODO: end

    procurement_production_ids = fields.One2many(
        'mrp.production', 'wave_id',
        string='Related productions', )

    # wave_id is for the pickings to supply
    procurement_picking_ids = fields.One2many(
        'stock.picking',  'procurement_wave_id',
        string='Related stock pickings', )

    procurement_purchase_ids = fields.One2many(
        'purchase.order', 'wave_id',
        string='Related purchases', )

    def _create_group_id(self):
        self.group_id = self.group_id.create({
            'name': self.name,
            'move_type': 'direct',
        })

    @api.multi
    def make_pending_procurements(self):
        for r in self:
            for m in r.make_procurement_ids:
                if m.qty == 0:
                    m.unlink()
                elif m.state == 'new':
                    m.sudo().make_procurement()

    @api.multi
    def supply_raw_materials(self):
        for wave in self:
            wave.supply_production_orders(target='raw')

    @api.multi
    def supply_semifinished_products(self):
        for wave in self:
            wave.supply_production_orders(target='semifinished')

    @api.multi
    def supply_production_orders(self, target=''):
        productions = self.procurement_production_ids.filtered(lambda x: x.state == 'confirmed')
        if target == 'raw':
            productions = productions.filtered(lambda x: not x.raw_ok)
        elif target == 'semifinished':
            productions = productions.filtered(lambda x: not x.semifinished_ok)

        products = {}
        for p in productions:
            check_loc = p.location_src_id
            wh = check_loc.get_warehouse(check_loc)
            moves = p.mapped('move_lines')
            if target == '':
                p.write({
                    'raw_ok': True,
                    'semifinished_ok': True,
                })
            else:
                raw, semifinished = self._separate_raw_and_semifinished(moves)
                if target == 'raw':
                    moves = raw
                    p.write({
                        'raw_ok': True,
                    })
                elif target == 'semifinished':
                    moves = semifinished
                    p.write({
                        'semifinished_ok': True,
                    })

            for m in moves:
                key, product = self.get_move_dict(m, wh)

                if key not in products:
                    products[key] = product
                else:
                    products[key]['product_uom_qty'] += product['product_uom_qty']
        self.create_procurements(products)

    @api.multi
    def _separate_raw_and_semifinished(self, moves):
        semifinished = self.env['stock.move']
        raw = self.env['stock.move']

        for m in moves:
            bom_obj = self.env['mrp.bom']
            product = m.product_id
            bom = bom_obj._bom_find(product.product_tmpl_id.id, product.id)
            m_bom = bom_obj.browse(bom)

            if not m_bom:
                raw += m
            else:
                semifinished += m
        return raw, semifinished

    @api.multi
    def button_supply(self):
        for wave in self:
            if not wave.group_id:
                wave._create_group_id()
            pickings = wave.picking_ids.filtered(lambda x: not x.procurement_ok)

            products = {}
            for p in pickings:
                check_loc = p.location_id
                wh = check_loc.get_warehouse(check_loc) or wave.warehouse_id.id
                moves = p.mapped('move_lines')

                for m in moves:
                    key, product = self.get_move_dict(m, wh)

                    if key not in products:
                        products[key] = product
                    else:
                        products[key]['product_uom_qty'] += product['product_uom_qty']

            wave.create_procurements(products)

            pickings.write({
                'procurement_ok': True,
            })

    def get_move_dict(self, m, wh):
        key = str(m.product_id.id) + '_' + str(m.product_uom.id) + '_' + str(wh)
        product = {
            'product_id': m.product_id.id,
            'product_uom_qty': m.product_uom_qty,
            'product_uom': m.product_uom.id,
            'product_tmpl_id': m.product_id.product_tmpl_id.id,
            'warehouse_id': wh,
            'product_variant_count': m.product_id.product_tmpl_id.product_variant_count
        }
        return key, product

    def create_procurements(self, products):
        quant_obj = self.env['stock.quant']
        prod_obj = self.env['product.product']
        procurements = []
        for product in products.values():
            prod_data = prod_obj.browse([product['product_id']])
            qty = product['product_uom_qty']
            if prod_data.mapped('mrp_mts_mto_location_ids'):
                location_ids = prod_data.mapped('mrp_mts_mto_location_ids').mapped('id')
                quant_data = quant_obj.search(
                    [('product_id', '=', prod_data.id),
                     ('location_id', 'in', location_ids),
                     ('reservation_id', '=', False)])
                quant = sum([x.qty for x in quant_data]) if len(quant_data) > 0 else 0.00
                qty -= quant
            procurements.append({
                'wave_id': self.id,
                'qty': qty,
                'product_id': product['product_id'],
                'product_tmpl_id': product['product_tmpl_id'],
                'product_variant_count': product['product_variant_count'],
                'uom_id': product['product_uom'],
                'warehouse_id': product['warehouse_id'],
                'date_planned': self.date_planned,
                'route_ids': '',
            })

        for p in procurements:
            self.env['make.procurement'].create(p)
