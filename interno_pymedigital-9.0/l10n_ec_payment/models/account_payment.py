# -*- coding: utf-8 -*-
from openerp import _, api, fields, models
from openerp.exceptions import UserError

from es_num2word import to_word


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_slip_number = fields.Char('Número de comprobante de pago', )
    payment_slip_file = fields.Binary('Archivo comprobante de pago', attachment=True, )
    secuencial = fields.Integer('Nro. Preimpreso', )

    check_city = fields.Char(string="Ciudad", )
    check_receiver = fields.Char(
        string="Beneficiario",
        help="Ingrese el nombre de la persona que cobrará el cheque en caso de ser distinta al proveedor o cliente.", )
    check_usetradename = fields.Boolean(
        string="Usar nombre comercial",
        help="Seleccione para imprimir el cheque usando el nombre comercial en lugar de la razón social.", )

    bank_id = fields.Many2one(
        'res.bank', string="Emisor",
        domain="[('credit_card_issuer','=',True)]",
        help="Entidad emisora de la tarjeta de crédito.",)

    @api.onchange('amount')
    def _onchange_amount(self):
        self.check_amount_in_words = to_word(self.amount)

    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()
        res.update(
            {
                'payment_slip_number': self.payment_slip_number,
                'payment_slip_file': self.payment_slip_file,
                'check_amount_in_words': self.check_amount_in_words,
                'check_city': self.check_city,
                'check_receiver': self.check_receiver,
                'check_usetradename': self.check_usetradename,
                'secuencial': self.secuencial,
            }
        )
        return res


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _default_city(self):
        return self.env.user.company_id.city or ''

    payment_slip_number = fields.Char('Comprobante Nro.', )
    payment_slip_file = fields.Binary('Archivo del comprobante', attachment=True, )
    secuencial = fields.Integer('Nro. Preimpreso', )
    check_city = fields.Char(string="Ciudad", default=_default_city)
    check_receiver = fields.Char(
        string="Beneficiario",
        help="Ingrese el nombre de la persona que cobrará el cheque en caso de ser distinta al proveedor o cliente.", )
    check_usetradename = fields.Boolean(
        string="Usar nombre comercial",
        help="Seleccione para imprimir el cheque usando el nombre comercial en lugar de la razón social.", )
    bank_id = fields.Many2one(
        'res.bank', string="Emisor",
        domain="[('credit_card_issuer','=',True)]",
        help="Entidad emisora de la tarjeta de crédito.",)
    efectivizado = fields.Boolean('Efectivizado', )
    contrapartida_id = fields.Many2one(
        'account.account', string="Contrapartida",
        domain="[('deprecated','=',False)]",
        help="Contrapartida para el registro del asiento contable. Ejm: Anticipo de proveedores, Anticipo de clientes.", )
    prepayment = fields.Boolean('¿es anticipo?', )

# METODOS REDEFINIDOS

    @api.multi
    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                # Reutilización de asiento.
                # move.unlink()
            rec.state = 'draft'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You can not delete a payment that is already posted"))
            # Reutilización de asiento.
            if rec.move_line_ids:
                rec.move_line_ids.mapped('move_id').unlink()
        return super(AccountPayment, self).unlink()

    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         # if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
    #         amount, self.currency_id, self.company_id.currency_id, invoice_currency)

    #     # Reutilización de asiento del pago
    #     if self.move_line_ids:
    #         moves = self.move_line_ids.mapped('move_id')
    #         for move in moves:
    #             for line in move.line_ids:
    #                 if line.reconciled:
    #                     line.remove_move_reconcile()
    #             move.line_ids.unlink()
    #     else:
    #         move = self.env['account.move'].create(self._get_move_vals())

    #     # Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(
    #         debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)

    #     # Reconcile with the invoices
    #     if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #         writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #         amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(
    #             self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
    #         # the writeoff debit and credit must be computed from the invoice residual in company currency
    #         # minus the payment amount in company currency, and not from the payment difference in the payment currency
    #         # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
    #         total_residual_company_signed = sum(
    #             invoice.residual_company_signed for invoice in self.invoice_ids)
    #         total_payment_company_signed = self.currency_id.with_context(
    #             date=self.payment_date).compute(self.amount, self.company_id.currency_id)
    #         if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
    #             amount_wo = total_payment_company_signed - total_residual_company_signed
    #         else:
    #             amount_wo = total_residual_company_signed - total_payment_company_signed
    #         debit_wo = amount_wo > 0 and amount_wo or 0.0
    #         credit_wo = amount_wo < 0 and -amount_wo or 0.0
    #         writeoff_line['name'] = _('Counterpart')
    #         writeoff_line['account_id'] = self.writeoff_account_id.id
    #         writeoff_line['debit'] = debit_wo
    #         writeoff_line['credit'] = credit_wo
    #         writeoff_line['amount_currency'] = amount_currency_wo
    #         writeoff_line['currency_id'] = currency_id
    #         writeoff_line = aml_obj.create(writeoff_line)
    #         if counterpart_aml['debit']:
    #             counterpart_aml['debit'] += credit_wo - debit_wo
    #         if counterpart_aml['credit']:
    #             counterpart_aml['credit'] += debit_wo - credit_wo
    #         counterpart_aml['amount_currency'] -= amount_currency_wo
    #     self.invoice_ids.register_payment(counterpart_aml)

    #     # Write counterpart lines
    #     if not self.currency_id != self.company_id.currency_id:
    #         amount_currency = 0
    #     liquidity_aml_dict = self._get_shared_move_line_vals(
    #         credit, debit, -amount_currency, move.id, False)
    #     liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #     aml_obj.create(liquidity_aml_dict)

    #     move.post()
    #     return move

    @api.one
    @api.depends('payment_method_code', 'invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.contrapartida_id:
            self.destination_account_id = self.contrapartida_id.id
        elif self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id

# FIN DE METODOS REDEFINIDOS

    @api.onchange('amount')
    def _onchange_amount(self):
        self.check_amount_in_words = to_word(self.amount)

    @api.onchange('prepayment')
    def _onchange_prepayment(self):
        if not self.prepayment:
            self.contrapartida_id = False

    @api.onchange('payment_method_code')
    def _onchange_payment_method_code(self):
        for r in self:
            if r.payment_method_code not in ('check_printing', 'tarjetacredito'):
                r.efectivizado = True
            # if r.prepayment == True:
                #company_id = self.env.user.company_id
                # if r.partner_type == 'customer':
                #r.contrapartida_id = r.partner_id.account_prepayments_customer_id or company_id.account_prepayments_customer_id
                # elif r.partner_type == 'supplier':
                #r.contrapartida_id = r.partner_id.account_prepayments_supplier_id or company_id.account_prepayments_supplier_id

    @api.multi
    def button_efectivizado(self):
        for r in self:
            r.efectivizado = True

    @api.multi
    def button_not_efectivizado(self):
        for r in self:
            r.efectivizado = False
