# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv
from stdnum.ec import ruc, ci
from stdnum.exceptions import *


class res_partner(osv.osv):
    _inherit = 'res.partner'

    @api.model
    def create_from_ui(self,  partner, context=None):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """

        # image is a dataurl, get the data after the comma
        if partner.get('image', False):
            img = partner['image'].split(',')[1]
            partner['image'] = img
        if partner.get('property_account_position_id', False):
            property_account_id = partner.get('property_account_position_id', False)

            fiscal=self.env['account.fiscal.position'].browse([int(property_account_id)])

            receivable = fiscal.property_account_receivable_id.id
            payable = fiscal.property_account_payable_id.id
            if not receivable:
                receivable = self.pool.get('account.account').search(cr, uid, [('internal_type', '=', 'receivable'),
                                                                               ('deprecated', '=', False)],
                                                                     context=context)[0]
            if not payable:
                payable = self.pool.get('account.account').search(cr, uid, [('internal_type', '=', 'payable'),
                                                                            ('deprecated', '=', False)],
                                                                  context=context)[0]

            partner['property_account_payable_id'] = receivable
            partner['property_account_receivable_id'] = payable
            partner['property_account_position_id'] = int(property_account_id)
            partner['do_check_vat'] = False

        partner_id = partner.pop('id', False)
        if partner_id:  # Modifying existing partner
            self.browse(partner_id).write(partner)
        else:
            partner_id = self.create(partner).id

        return partner_id

    def sri_check_vat_from_ui_pos(self, cr, uid, partner, context=None):
        log_error = False

        if partner.get('property_account_position_id', False):
            property_account_id = partner.get('property_account_position_id', False)
            fiscal = self.pool.get('account.fiscal.position').browse(cr, uid, [int(property_account_id)],
                                                                     context=context)
            partner['do_check_vat'] = True

        if partner['do_check_vat']:

            persona = fiscal.persona_id.code
            identificacion = fiscal.identificacion_id.code
            if partner['vat'] and fiscal:
                try:
                    if identificacion == 'R':
                        # Verificación de tipo de contribuyente
                        if persona == '6' and partner['vat'][2:3] < '6':
                            pass
                        elif persona == '9' and partner['vat'][2:3] == '6' and fiscal.es_publica:
                            pass
                        elif persona == '9' and partner['vat'][2:3] == '9' and not fiscal.es_publica:
                            pass
                        else:
                            return (_("El numero de R.U.C. o C.I. no concuerda con el tipo de "
                                              "contribuyente, por favor verifique que el numero sea correcto "
                                              "en la página www.sri.gob.ec"))
                        # Verificación del documento
                        ruc.validate(partner['vat'])
                    elif identificacion == 'C':
                        ci.validate(partner['vat'])
                except InvalidChecksum:
                    return (_("El numero de R.U.C. o C.I. no concuerda con el proceso de validacion "
                                      "del S.R.I., por favor verifique que el numero sea correcto en la "
                                      "página www.sri.gob.ec"))
                except InvalidComponent:
                    if identificacion == 'R':
                        return (_("El numero de R.U.C. contiene errores, por favor verifique que "
                                          "los dos primeros dígitos se encuentren entre 01 y 24, que el tercer"
                                          "tercero digito no sea mayor que 5 y que el número de establecimiento sea"
                                          "válido."))
                    elif identificacion == 'C':
                        return (_("El numero de C.I. contiene errores, por favor verifique que "
                                          "los dos primeros dígitos se encuentren entre 01 y 24, que el tercer"
                                          "tercero digito no sea mayor que 5."))
                except InvalidLength:
                    if identificacion == 'R':
                        return (_("El numero de R.U.C. debe tener 13 digitos, por favor verifique la "
                                          "información ingresada."))
                    elif identificacion == 'C':
                        return (_("El numero de C.I. debe tener 10 digitos, por favor verifique la "
                                          "información ingresada."))
                except InvalidFormat:
                    return (_("El numero de R.U.C. o C.I. tiene caracteres no válidos, por favor "
                                      "verfique que la información ingresada sea correcta."))
        else:
            return log_error

    # def check_vat_from_ui(self, cr, uid, property_account_position_id, vat, context=None):
    #     fiscal = self.pool.get('account.fiscal.position').browse(cr, uid, [int(property_account_position_id)],
    #                                                              context=context)
    #     persona = fiscal.persona_id.code
    #     identificacion = fiscal.identificacion_id.code
    #     if vat and fiscal:
    #         try:
    #             if identificacion == 'R':
    #                 # Verificación de tipo de contribuyente
    #                 if persona == '6' and vat[2:3] < '6':
    #                     pass
    #                 elif persona == '9' and vat[2:3] == '6' and fiscal.es_publica:
    #                     pass
    #                 elif persona == '9' and vat[2:3] == '9' and not fiscal.es_publica:
    #                     pass
    #                 else:
    #                     return "El numero de R.U.C. o C.I. no concuerda con el tipo de \
    #                     contribuyente, por favor verifique que el numero sea correcto \
    #                     en la página www.sri.gob.ec"
    #                     # Verificación del documento
    #             ruc.validate(vat)
    #             if identificacion == 'C':
    #                 ci.validate(vat)
    #         except InvalidChecksum:
    #             return "El numero de R.U.C. o C.I. no concuerda con el proceso de validacion del S.R.I., por favor verifique que el numero sea correcto en la página www.sri.gob.ec"
    #         except InvalidComponent:
    #             if identificacion == 'R':
    #                 return "El numero de R.U.C. contiene errores, por favor verifique que los dos primeros dígitos se encuentren entre 01 y 24, que el tercero digito no sea mayor que 5 y que el n�mero de establecimiento sea válido"
    #             if identificacion == 'C':
    #                 return "El numero de C.I. contiene errores, por favor verifique que los dos primeros dígitos se encuentren entre 01 y 24, que el tercer digito no sea mayor que 5."
    #         except InvalidLength:
    #             if identificacion == 'R':
    #                 return "El numero de R.U.C. debe tener 13 digitos, por favor verifique la información ingresada"
    #             if identificacion == 'C':
    #                 return "El numero de C.I. debe tener 10 digitos, por favor verifique la información ingresada."
    #         except InvalidFormat:
    #             return "El numero de R.U.C. o C.I. tiene caracteres no válidos, por favor verfique que la información ingresada sea correcta."
