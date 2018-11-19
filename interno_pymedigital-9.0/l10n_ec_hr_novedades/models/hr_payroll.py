# -*- coding: utf-8 -*-
from openerp import models, api, _

class hr_payslip(models.Model):
    _inherit = ['hr.payslip']

    @api.model
    def hr_verify_sheet(self):
        super(hr_payslip, self).hr_verify_sheet()
        novedades = self.input_line_ids.mapped('novedad_id')
        if novedades:
            novedades.write({'state': 'pagado'})

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, context=None):
        contract_obj = self.pool.get('hr.contract')
        res = super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=None)
        novedad_line_obj = self.pool.get('hr.novedad.line')
        he_line_obj = self.pool.get('hr.he.line')
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            novedad_ids = novedad_line_obj.search(cr, uid, [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('employee_id', '=', contract.employee_id.id),
                ('state', '=', 'pendiente'),
            ])
            for novedad in novedad_line_obj.browse(cr, uid, novedad_ids, context=context):
                inputs = {
                    'name': unicode(novedad.name or novedad.rule_id.name).upper(),
                    'code': novedad.rule_id.code,
                    'contract_id': contract.id,
                    'novedad_id': novedad.id,
                    'amount': novedad.amount,
                }
                res += [inputs]
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            he_ids = he_line_obj.search(cr, uid, [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('employee_id', '=', contract.employee_id.id),
                ('state', '=', 'done'),
            ])
            for he in he_line_obj.browse(cr, uid, he_ids, context=context):
                if he.he_id.state == 'done' and he.total != 0:
                    if he.hora_125 > 0:
                        inputs = {
                            'name': _('Hour 25%'),
                            'code': 'ALW',
                            'contract_id': contract.id,
                            'amount': (he.valor_hora * he.hora_125 * 1.25),
                        }
                        res += [inputs]
                    if he.hora_150 > 0:
                        inputs = {
                            'name': _('Hour 50%'),
                            'code': 'ALW',
                            'contract_id': contract.id,
                            'amount': (he.valor_hora * he.hora_150 * 1.50),
                        }
                        res += [inputs]
                    if he.hora_200 > 0:
                        inputs = {
                            'name': _('Hour 100%'),
                            'code': 'ALW',
                            'contract_id': contract.id,
                            'amount': (he.valor_hora * he.hora_200 * 2.0),
                        }
                        res += [inputs]
        return res