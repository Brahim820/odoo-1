# -*- coding: utf-8 -*-
from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = ['account.invoice']

    invoice_ats_errors = fields.Char('Validaciones ATS', store=True, )
    invoice_ats_exception = fields.Boolean('Ignorar advertencias', )

    @api.multi
    def button_sri_ats_checker(self):
        for inv in self:
            if not inv.invoice_ats_exception:
                inv.get_ats_errors()

    @api.multi
    def get_ats_errors(self):
        retenciones = ('RetAir', 'RetIva', 'RetBien10',
                       'RetBienes', 'RetServ50', 'RetServ100',
                       'RetServ20', 'RetServicios')
        impuestos = ('ImpExe', 'ImpGrav', 'Imponible',
                     'Reembolso', 'NoGraIva',)

        for inv in self:
            errors = u''

            # DOCUMENTOS DUPLICADOS.
            # Buscamos sencuenciales duplicadas.
            # duplicados = self.search([
            #    ('type', '=', inv.type),
            #    ('secuencial', '=', inv.secuencial),
            #])

            # Si el secuencial está duplicado aplicamos los demás filtros.
            # duplicados = duplicados.search([
            #    ('autorizacion', '=', inv.autorizacion),
            #    ('establecimiento', '=', inv.establecimiento),
            #    ('puntoemision', '=', inv.puntoemision),
            #    ('company_id', '=', inv.company_id.id),
            #    ('id', '!=', inv.id)])

            # Si es documento de tercero, comprobamos el partner.
            # if inv.type in ('in_invoice', 'in_refund'):
            #    duplicados = duplicados.search([('partner_id', inv.partner_id.id)])

            # if duplicados:
            #    errors += 'La factura parece ser duplicada de %s. ' % duplicados

            # VALIDACIONES DEL TIPO DE COMPROBANTE

            if inv.comprobante_id.code in ('NA', False):
                # Si la factura no tiene un comprobante válido no puede tener impuestos.
                if inv.tax_line_ids:
                    errors += u'- El documento registra impuestos pero no registra un comprobante con valor tributario.'
                else:
                    errors += u'- Este documento no se considerará en sus declaraciones. '
            else:
                # Si tiene un comprobante válido, debe tener al menos un impuesto a declarar.
                if not inv.invoice_line_ids.mapped('invoice_line_tax_ids'):
                    errors += u'- El documento registra un comprobante con valor tributario, pero no registra impuestos.'

            # VALIDACIONES DE LA RETENCIÓN
            ret_amount = sum(inv.sri_tax_line_ids.filtered(lambda x: x.group in retenciones).mapped('amount'))

            # Los datos del comprobante de retención son necesarios solo cuando hay valor de retención.
            if ret_amount > 0:

                # TODO: Borrar una vez que el sistema esté registrando bien estos datos.
                # En caso de que no haya valores en la factura, pero haya una autorización
                # agregamos los datos de la autorización pues es un error por el onchange.
                if inv.r_autorizacion_id:
                    if not inv.estabretencion1:
                        inv.estabretencion1 = inv.r_autorizacion_id.establecimiento
                    if not inv.ptoemiretencion1:
                        inv.ptoemiretencion1 = inv.r_autorizacion_id.puntoemision
                    if not inv.autretencion1:
                        inv.autretencion1 = inv.r_autorizacion_id.autorizacion
                    if not inv.r_comprobante_id:
                        inv.r_comprobante_id = inv.r_autorizacion_id.comprobante_id
                # TODO: END

                if not inv.estabretencion1 or len(inv.estabretencion1) != 3 or int(inv.estabretencion1) < 1:
                    errors += u'- Establecimiento del comprobante de retención inválido.\n'
                if not inv.ptoemiretencion1 or len(inv.ptoemiretencion1) != 3 or int(inv.ptoemiretencion1) < 1:
                    errors += u'- Punto de emisión del comprobante de retención inválido.\n'
                if not inv.autretencion1 or len(inv.autretencion1) not in (10, 37, 49):
                    errors += u'- La autorización del comprobante de retención debe tener 10, 37 o 49 dígitos.\n'
                if not inv.fechaemiret1 or inv.date_invoice > inv.fechaemiret1:
                    errors += u'- La fecha del comprobante de retención debe ser mayor a la fecha del comprobante.\n '
                if not inv.secretencion1 or len(inv.secretencion1) > 9 or int(inv.secretencion1) < 1:
                    errors += u'- El secuencial de la retención debe tener menos de 10 caracteres y ser distinto de cero.\n '

            for line in inv.invoice_line_ids:
                # Si tiene retenciones, aunque esten en cero, debe haber un registro con la base.
                if any(tax.tax_group_id.name in retenciones for tax in line.invoice_line_tax_ids):
                    if not any(tax.tax_group_id.name in impuestos for tax in line.invoice_line_tax_ids):
                        errors += u'- Si registra una retención debe registrar el impuesto de la base imponible.\n'

            # TODO: Borrar una vez que el sistema esté registrando bien estos datos.
            # En caso de que no haya valores en la factura, pero haya una autorización
            # agregamos los datos de la autorización pues es un error por el onchange.
            if inv.autorizacion_id:
                inv.tipoem = inv.autorizacion_id.tipoem
                if not inv.establecimiento:
                    inv.establecimiento = inv.autorizacion_id.establecimiento
                if not inv.puntoemision:
                    inv.puntoemision = inv.autorizacion_id.puntoemision
                if not inv.autorizacion:
                    inv.autorizacion = inv.autorizacion_id.autorizacion
                if not inv.comprobante_id:
                    inv.comprobante_id = inv.autorizacion_id.comprobante_id
            # TODO END.

            if not inv.establecimiento or len(inv.establecimiento) != 3 or int(inv.establecimiento) < 1:
                errors += u'- Establecimiento inválido.\n'
            if not inv.puntoemision or len(inv.puntoemision) != 3 or int(inv.puntoemision) < 1:
                errors += u'- Punto de emisión inválido.\n'
            if not inv.autorizacion or len(inv.autorizacion) not in (10, 37, 49):
                errors += u'- La autorización debe tener 10, 37 o 49 dígitos.\n'
            if not inv.secuencial or len(inv.secuencial) > 9 or int(inv.secuencial) < 1:
                errors += u'- El secuencial debe tener menos de 10 caracteres y ser distinto de cero.\n'

            # VALIDACIÓN DE REEMBOLSOS
            # Si tiene sustento tributario de reembolso.
            #r = ['08', '06']
            # if any(x in inv.codsustento for x in r) and not inv.reembolso_ids:
            #    errors += 'El documento registra sustentos tributarios de reembolso (06 o 08) pero no registra documentos reembolsados. '

            # Si tiene una base imponible de reembolso.
            # if inv.basereembolso:
            #    if inv.comprobante_id.code != '41':
            #        errors += 'Los comprobantes de venta emitidos por reembolso deben tener código 41. '
            #    if not inv.documento_reembolsado_ids:
            #        errors += 'El documento contiene valores por reembolso pero no se registra el comprobante que fué reembolsado. '

            # Valida datos del partner
            if not inv.partner_id.vat:
                errors += u'- El cliente o proveedor no tiene registrado ruc o cédula.\n'
            if not inv.partner_id.property_account_position_id:
                errors += u'- El cliente o proveedor no tiene registrada la posisión fiscal.\n'

            inv.invoice_ats_errors = errors
