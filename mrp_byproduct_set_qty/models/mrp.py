# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import _, api, fields, models
from openerp.tools import float_compare, float_is_zero


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    produce = fields.Integer('Produce id')

    @api.v7
    def _get_subproduct_factor(self, cr, uid, production_id, move_id=None, context=None):
        res = super(MrpProduction, self)._get_subproduct_factor(
            cr, uid, production_id, move_id, context=context)
        mrp = self.pool.get('mrp.production').browse(cr, uid, production_id, context=context)
        produce = mrp.produce
        wiz = self.pool.get('mrp.product.produce').browse(cr, uid, produce, context=context)
        move = self.pool.get('stock.move').browse(cr, uid, move_id, context=context)
        product = move.product_id

        for sp in wiz.subproduct_created_ids:
            if sp.product_id.id == product.id:
                res = sp.product_uom_qty / wiz.product_qty
        return res

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(
            cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        main_production_move = False
        if production_mode == 'consume_produce':
            for produce_product in production.move_created_ids:
                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

        total_consume_moves = set()
        if production_mode in ['consume', 'consume_produce']:
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'product_id': cons.product_id.id,
                                          'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(
                    cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    if raw_material_line.state in ('done', 'cancel'):
                        continue
                    if remaining_qty <= 0:
                        break
                    if consume['product_id'] != raw_material_line.product_id.id:
                        continue
                    consumed_qty = min(remaining_qty, raw_material_line.product_qty)
                    stock_mov_obj.action_consume(cr, uid, [raw_material_line.id], consumed_qty, raw_material_line.location_id.id,
                                                 restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                    total_consume_moves.add(raw_material_line.id)
                    remaining_qty -= consumed_qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(
                        cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(
                        cr, uid, production, product, product.uom_id.id, remaining_qty, context=context)
                    stock_mov_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': consume['lot_id'],
                                                                   'consumed_for': main_production_move}, context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)
                    total_consume_moves.add(extra_move_id)

        if production_mode == 'consume_produce':
            # add production lines that have already been consumed since the last 'consume & produce'
            last_production_date = production.move_created_ids2 and max(
                production.move_created_ids2.mapped('date')) or False
            already_consumed_lines = production.move_lines2.filtered(
                lambda l: l.date > last_production_date)
            total_consume_moves = total_consume_moves.union(already_consumed_lines.ids)

            price_unit = 0
            for produce_product in production.move_created_ids:
                is_main_product = (produce_product.product_id.id ==
                                   production.product_id.id) and production.product_id.cost_method == 'real'
                if is_main_product:
                    total_cost = self._calculate_total_cost(
                        cr, uid, list(total_consume_moves), context=context)
                    production_cost = self._calculate_workcenter_cost(
                        cr, uid, production_id, context=context)
                    price_unit = (total_cost + production_cost) / production_qty_uom

                subproduct_factor = self._get_subproduct_factor(
                    cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    lot_id = wiz.lot_id.id
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) #Needed when producing more than maximum quantity


                # Verificamos si hay una línea de subproducto y si hay una diferencia.
                subproduct_diff = 0
                subproduct_line = self.pool.get('mrp.subproduct.produce.line')
                if produce_product.product_id != production.product_id:
                    subproduct_line = wiz.subproduct_created_ids.filtered(lambda x: x.product_id == produce_product.product_id)
                    subproduct_qty = subproduct_line.product_uom_qty
                    if subproduct_qty > qty:
                        subproduct_diff = subproduct_qty - qty
                    else:
                        qty = subproduct_qty
                elif production_qty > produce_product.product_uom_qty:
                    subproduct_diff = production_qty - produce_product.product_uom_qty

                if is_main_product and price_unit:
                    stock_mov_obj.write(cr, uid, [produce_product.id], {
                                        'price_unit': price_unit}, context=context)
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {
                                    'production_id': production_id}, context=context)

                remaining_qty = subproduct_diff

                remaining_qty = subproduct_diff
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    # consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    if is_main_product:
                        stock_mov_obj.write(cr, uid, [extra_move_id], {
                                            'price_unit': price_unit}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

        self.message_post(cr, uid, production_id, body=_("%s produced") %
                          self._description, context=context)

        # Remove remaining products to consume if no more products to produce
        # Verificamos los valores pendientes de producción solamente contra el producto principal.

        main_product_remaining = production.move_created_ids.filtered(
            lambda x: x.product_id == production.product_id)
        if not main_product_remaining:
            if production.move_lines:
                stock_mov_obj.action_cancel(
                    cr, uid, [x.id for x in production.move_lines], context=context)
            if production.move_created_ids:
                stock_mov_obj.action_cancel(
                    cr, uid, [x.id for x in production.move_created_ids], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True
