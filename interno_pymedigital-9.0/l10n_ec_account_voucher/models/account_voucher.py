# -*- coding: utf-8 -*-
from openerp import models, api, _
from openerp.exceptions import UserError


class account_voucher_line(models.Model):
    _inherit = 'account.voucher.line'

    @api.multi
    def product_id_change(self, product_id, partner_id=False, price_unit=False, company_id=None, currency_id=None, type=None):
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)
        if not partner_id:
            raise UserError(_("You must first select a partner!"))
        part = self.env['res.partner'].browse(partner_id)
        if part.lang:
            self = self.with_context(lang=part.lang)

        product = self.env['product.product'].browse(product_id)
        fpos = part.property_account_position_id
        account = self._get_account(product, fpos, type)
        values = {
            'name': product.partner_ref,
            'account_id': account.id,
        }

        if type == 'purchase':
            values['price_unit'] = price_unit or product.standard_price
            taxes = product.supplier_taxes_id or account.tax_ids
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase
        else:
            values['price_unit'] = product.lst_price
            taxes = product.taxes_id or account.tax_ids
            if product.description_sale:
                values['name'] += '\n' + product.description_sale

        values['tax_ids'] = taxes.ids

        if company and currency:
            if company.currency_id != currency:
                if type == 'purchase':
                    values['price_unit'] = product.standard_price
                values['price_unit'] = values['price_unit'] * currency.rate

        return {'value': values, 'domain': {}}
