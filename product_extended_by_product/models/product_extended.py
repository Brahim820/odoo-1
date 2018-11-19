# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv


class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'

    def compute_price(
            self, cr, uid, product_ids, template_ids=False,
            recursive=False, test=False, real_time_accounting = False, context=None):
        '''
        Will return test dict when the test = False
        Multiple ids at once?
        testdict is used to inform the user about the changes to be made
        '''
        testdict = {}
        if product_ids:
            ids = product_ids
            model = 'product.product'
        else:
            ids = template_ids or []
            model = 'product.template'
        for prod_id in ids:
            bom_obj = self.pool.get('mrp.bom')

            prod_obj = self.browse(cr, uid, prod_id, context=context)
            bom_id = prod_obj.default_bom_id.id

            if not bom_id:
                if model == 'product.product':
                    bom_id = bom_obj._bom_find(
                        cr, uid, product_id=prod_id, context=context)
                else:
                    bom_id = bom_obj._bom_find(
                        cr, uid, product_tmpl_id=prod_id, context=context)
            if bom_id:
                # In recursive mode, it will first compute the prices of child boms
                if recursive:
                    #Search the products that are components of this bom of prod_id
                    bom = bom_obj.browse(cr, uid, bom_id, context=context)

                    #Call compute_price on these subproducts
                    prod_set = set([x.product_id.id for x in bom.bom_line_ids])
                    res = self.compute_price(
                        cr, uid, list(prod_set),
                        recursive=recursive,
                        test=test,
                        real_time_accounting = real_time_accounting,
                        context=context)
                    if test:
                        testdict.update(res)
                #Use calc price to calculate and put the price on the product of the BoM if necessary
                price = self._calc_price(
                    cr, uid,
                    bom_obj.browse(cr, uid, bom_id, context=context),
                    test=test,
                    real_time_accounting = real_time_accounting,
                    context=context)
                if test:
                    testdict.update({prod_id : price})
        if test:
            return testdict
        else:
            return True

    def _calc_price(self, cr, uid, bom, test = False, real_time_accounting=False, context=None):
        if context is None:
            context={}
        price = 0
        uom_obj = self.pool.get("product.uom")
        tmpl_obj = self.pool.get('product.template')
        for sbom in bom.bom_line_ids:
            my_qty = sbom.product_qty / sbom.product_efficiency
            if not sbom.attribute_value_ids:
                # No attribute_value_ids means the bom line is not variant specific
                price += uom_obj._compute_price(
                    cr, uid, sbom.product_id.uom_id.id,
                    sbom.product_id.standard_price,
                    sbom.product_uom.id) * my_qty

        if bom.routing_id:
            for wline in bom.routing_id.workcenter_lines:
                wc = wline.workcenter_id
                cycle = wline.cycle_nbr
                hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
                price += wc.costs_cycle * cycle + wc.costs_hour * hour
                price = self.pool.get('product.uom')._compute_price(
                    cr,uid,bom.product_uom.id, price, bom.product_id.uom_id.id)

        subproduct_weight = sum(sp.price_weight for sp in bom.sub_products)

        if subproduct_weight:
            bom_price = 0
            bom_price += price
            price = price * ((100 - subproduct_weight) / 100.0)

            for sp in bom.sub_products:
                if not sp.price_weight:
                    continue

                sp_tmpl = sp.product_id.product_tmpl_id
                if (sp_tmpl.valuation != "real_time" or not real_time_accounting):
                    sp_price = bom_price * ((sp.price_weight) / 100.0)
                    if sp_price > 0:
                        sp_price = sp_price / sp.product_qty
                        tmpl_obj.write(
                            cr, uid, [sp_tmpl.id], {'standard_price' : sp_price},
                            context=context)

        #Convert on product UoM quantities
        if price > 0:
            price = uom_obj._compute_price(
                cr, uid, bom.product_uom.id,
                price / bom.product_qty,
                bom.product_id.uom_id.id)

        product = tmpl_obj.browse(cr, uid, bom.product_tmpl_id.id, context=context)
        if not test:
            if (product.valuation != "real_time" or not real_time_accounting):
                tmpl_obj.write(cr, uid, [product.id], {'standard_price' : price}, context=context)
            else:
                #Call wizard function here
                wizard_obj = self.pool.get("stock.change.standard.price")
                ctx = context.copy()
                ctx.update({'active_id': product.id, 'active_model': 'product.template'})
                wiz_id = wizard_obj.create(cr, uid, {'new_price': price}, context=ctx)
                wizard_obj.change_price(cr, uid, [wiz_id], context=ctx)
        return price
