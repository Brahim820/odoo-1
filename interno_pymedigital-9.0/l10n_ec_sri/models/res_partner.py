# -*- coding: utf-8 -*-
from openerp import api, fields, models


ADDRESS_FIELDS = ('vat', 'street', 'street2', 'zip', 'city', 'state_id', 'country_id')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _display_address(self, cr, uid, address, without_company=False, context=None):
        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = """%(vat)s\n%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s \n%(phone)s \n%(mobile)s"""
        args = {
            'vat': address.vat or '',
            'street': address.street or '',
            'street2': address.street2 or '',
            'city': address.city or '',
            'zip': address.zip or '',
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
            'phone': address.phone or '',
            'mobile': address.mobile or ''
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    def _address_fields(self, cr, uid, context=None):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        return list(ADDRESS_FIELDS)

    def _default_country_id(self):
        country = self.env['res.country'].search([('code', '=ilike', 'EC')])
        return country

    country_id = fields.Many2one(default=_default_country_id, )

    vat = fields.Char('Identificacion fiscal', size=13, required=True)
    formapago_id = fields.Many2one(
        'l10n_ec_sri.formapago', string='Forma de pago principal', )
    parterel = fields.Boolean(
        string="¿Es parte relacionada?", copy=False, )

    @api.onchange('property_account_position_id')
    def _onchange_property_account_position(self):
        if self.property_account_position_id:
            fiscal = self.property_account_position_id
            receivable = fiscal.property_account_receivable_id
            payable = fiscal.property_account_payable_id

            if not self.property_account_payable_id:
                self.property_account_payable_id = payable
            if not self.property_account_receivable_id:
                self.property_account_receivable_id = receivable
