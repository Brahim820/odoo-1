# -*- coding: utf-8 -*-

from openerp import _, api, fields, models

from dateutil.relativedelta import relativedelta


class MrpProductionRequestCreateMo(models.TransientModel):
    _inherit = "mrp.production.request.create.mo"

    mo_distributed_qty = fields.Text('Distributed productions', )
    routing_id = fields.Many2one(comodel_name='mrp.routing', string='Alternative Routing', )
    date_start = fields.Datetime('Date to start', default=fields.datetime.now(), required=True, )
    date_step = fields.Integer('Date Step', default=1, required=True, )
    mo_distribution_method = fields.Selection([
        ('opt', 'Optimus production qty'),
        ('min', 'Minimum production qty'),
        ('max', 'Maximum production qty'),
    ], default='opt', required=True, )

    @api.multi
    def compute_mo_distributed_qty(self):
        request_id = self.mrp_production_request_id
        pending_qty = self.pending_qty
        bom = request_id.bom_id
        uom = request_id.product_uom
        route = self.routing_id or request_id.routing_id
        method = self.mo_distribution_method
        date = fields.Datetime.from_string(self.date_start)
        step = self.date_step

        if route:
            min_qty, max_qty, opt_qty = bom.compute_production_qty(
                route=route, uom=uom, product=request_id.product_id)
        else:
            min_qty = max_qty = opt_qty = pending_qty

        uom_qty = pending_qty
        if method == 'opt':
            uom_qty = opt_qty
        elif method == 'min':
            uom_qty = min_qty
        elif method == 'max':
            uom_qty = max_qty

        productions = int(pending_qty // uom_qty)
        pending = pending_qty % uom_qty

        last = 0
        if pending > 0:
            if uom_qty + pending < max_qty:
                productions = productions - 1
                last = uom_qty + pending
            elif pending > min_qty:
                last = pending
            else:
                last = min_qty

        mo_distributed_qty = ''
        if productions > 0:
            for i in range(0, productions):
                mo_distributed_qty += str(uom_qty) + ' / ' + date.strftime('%Y-%m-%d') + '\n'
                date = date + relativedelta(days=step)
        if last > 0:
            mo_distributed_qty += str(last) + ' / ' + date.strftime('%Y-%m-%d')

        self.mo_distributed_qty = mo_distributed_qty

    @api.multi
    def compute_product_line_ids(self):
        res = super(MrpProductionRequestCreateMo, self).compute_product_line_ids()
        self.compute_mo_distributed_qty()
        return res

    @api.multi
    def create_distributed_mo(self):
        if self.mo_distributed_qty:
            time = self.date_start[10:]
            productions = self.mo_distributed_qty.split('\n')
            productions.remove('')
            for p in productions:
                product_qty, date = p.split(' / ')
                print 'production', p, product_qty, date, 'MERGE DATE', date

                vals = self._prepare_manufacturing_order()
                vals.update({
                    'product_qty': float(product_qty),
                    'date_planned': date + time
                })

                if self.routing_id:
                    vals.update({
                        'routing_id': self.routing_id.id,
                        'state': 'confirmed'
                    })

                self.env['mrp.production'].create(vals)
