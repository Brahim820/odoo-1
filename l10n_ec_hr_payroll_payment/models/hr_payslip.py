# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    payment_ids = fields.One2many('account.payment', 'payroll_slip_run_id', string=_('Payments'))
    state = fields.Selection(selection_add=[('paid', _('Paid'))])


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def _compute_pay_amount(self):
        line_obj = self.env['hr.payslip.line']
        # TODO LIQ se deja por compatibilidad, una vez pagados los sueldos con LIQ, dejar solo NET.
        liquido = line_obj.search([('code', 'in', ('NET', 'LIQ')), ('slip_id', '=', self.id)])
        self.pagar_liquido = liquido.amount

    @api.multi
    def pay_sheet(self):
        valor = self.pagar_liquido
        account_payable_id = self.employee_id.account_sueldos_id or self.employee_id.address_home_id.property_account_payable_id
        payment_form = self.env.ref('l10n_ec_payment.view_account_payment_form_ec', False)
        ctx = {
            'default_model': 'hr.payslip',
            'default_partner_id': self.employee_id.address_home_id.id,
            'default_partner_type': 'supplier',
            'default_payment_type': 'outbound',
            'default_amount': valor,
            'default_contrapartida_id': account_payable_id.id,
            'default_communication': self.number,
            'default_payment_reference': self.name,
            'default_payroll_slip_id': self.id,
            #'default_payment_method_id': self.journal_id.id,
            'default_journal_id': self.journal_id.id,

        }
        return {
            'name': 'Pagar rol',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'res_id': False,
            'views': [(payment_form.id, 'form')],
            'view_id': payment_form.id,
            'target': 'new',
            'context': ctx,
        }

    # TODO: refund_sheet: Control de estado del asiento de pago,
    # TODO: refund_sheet: depuración de error actual

    @api.model
    def _compute_paid_state(self):
        self.paid = False
        if self.payment_id:
            self.paid = True

    @api.model
    def _conciliate_sheet(self):
        if not self.reconciled and self.payment_id:
            # Buscar referencia de rol, partner_id y cuenta de salario.
            account_payable_id = self.employee_id.account_sueldos_id.id or self.employee_id.address_home_id.property_account_payable_id.id
            partner_id = self.employee_id.address_home_id.id
            ref = self.number
            move_line_obj = self.env['account.move.line']
            lines = move_line_obj.search([('account_id', '=', account_payable_id),
                                          ('partner_id', '=', partner_id),
                                          ('ref', '=', ref),
                                          ('reconciled', '=', True)])
            if len(lines) > 1:
                lines.reconcile()
                self.reconciled = True
            else:
                UserWarning('Error', 'Error')

    pagar_liquido = fields.Float('Liquido a pagar', help='El valor a pagar al empleado',
                                 compute='_compute_pay_amount')
    paid = fields.Boolean('Made Payment Order ? ',
                          required=False,
                          readonly=True,
                          states={'draft': [('readonly', False)]},
                          copy=False,
                          compute="_compute_paid_state")
    reconciled = fields.Boolean('Conciliado', copy=False,
                                compute="_conciliate_sheet",
                                help="Indica sí el rol ha sido conciliado")
    payment_id = fields.One2many('account.payment', 'payroll_slip_id', string='Pago')
