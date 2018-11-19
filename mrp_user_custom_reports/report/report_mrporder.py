# -*- coding: utf-8 -*-

import time
from openerp import api, models

class ReportMRPOrder(models.AbstractModel):
    _name = 'report.mrp_user_custom_reports.report_mrporder'

    _inherit = 'bi.mrp.report.wizard'

    @api.multi
    def get_resume_lines(self, mporder):
        lines = []
        subproduct_lines = []
        if not (mporder is None):

            mp_production_lines, mp_positions = self.get_production_report_detail(mporder, False)

            for li in mp_production_lines:
                if li[mp_positions['mp_name']] != '':
                    lines.append({
                        # 'product_id': li.product_id.id,
                        'product_name': li[mp_positions['mp_name']],
                        'product_code': li[mp_positions['mp_code']],
                        'uom_name': li[mp_positions['mp_uom_name']],
                        'planned_qty': li[mp_positions['mp_planificada']],
                        'product_uom_qty': li[mp_positions['mp_consumida']],
                        'diff_qty': li[mp_positions['mp_diferencia']],
                        'scrap_qty': li[mp_positions['mp_desechada']]
                    });
                else:
                    subproduct_lines.append({
                        'product_name': li[mp_positions['subproducto_nombre']],
                        'product_code': li[mp_positions['subproducto_codigo']],
                        'uom_name': li[mp_positions['subproducto_uom']],
                        'planned_qty': li[mp_positions['subproducto_plan']],
                        'product_uom_qty': li[mp_positions['subproducto_real']],
                        'diff_qty': li[mp_positions['subproducto_diff']],
                    });

            # for li in mporder.product_lines:
            #     line = {
            #         'product_id': li.product_id.id,
            #         'product_name': li.product_id.name,
            #         'uom_name': li.product_uom.name,
            #         'planned_qty': li.product_qty,
            #         'product_uom_qty': 0.0,
            #         'diff_qty': 0.0
            #     }
            #     by_products = mporder.move_lines.filtered(
            #         lambda l: l.product_id == li.product_id)
            #
            #     if len(by_products) > 0:
            #         for li2 in by_products:
            #             line['diff_qty'] += li2.product_uom_qty
            #
            #         line['product_uom_qty'] = line['planned_qty'] - line['diff_qty']
            #     else:
            #         by_products = mporder.move_lines2.filtered(
            #             lambda l: l.product_id != li.product_id)
            #
            #         for li2 in by_products:
            #             line['product_uom_qty'] += li2.product_uom_qty
            #
            #         line['diff_qty'] = line['planned_qty'] - line['product_uom_qty']
            #
            #     lines.append(line);
        return lines, subproduct_lines;

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('mrp_user_custom_reports.report_mrporder')
        docs = self.env[report.model].browse(self.id)

        resume_lines, subproduct_lines = self.get_resume_lines(docs)
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': docs,
            'resume_lines': resume_lines,
            'subproduct_lines': subproduct_lines,
        }
        return report_obj.render('mrp_user_custom_reports.report_mrporder', docargs)