# -*- coding: utf-8 -*-
import unicodedata  # para normalizar el nombre
from collections import OrderedDict
from datetime import datetime

import pytz
from openerp import _, api, fields, models
from openerp.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def get_detallesadicionales(self):
        """
        return: [(nombre,valor),(nombre,valor)]
        """
        return []


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_custom_attachments(self):
        """
        Enviamos el documento electrónico de acuerdo al tipo
        para evitar errores en el envío.

        return: [('nombre_completo.ext','base64string')]
        """
        try:
            attachments = super(AccountInvoice, self)._get_custom_attachments()
        except:
            attachments = []
        if self.type == 'out_invoice':
            attachment_id = self.factura_electronica_id
        if self.type == 'in_invoice':
            attachment_id = self.retencion_electronica_id
        if self.type == 'out_refund':
            attachment_id = self.nota_credito_electronica_id

        if attachment_id:
            attachments.append(
                (attachment_id.xml_filename, attachment_id.xml_file)
            )
        return attachments

    @api.multi
    def get_days(self, inv):
        date_format = '%Y-%m-%d'
        res = 0
        if inv:
            date_invoice = datetime.strptime(inv.date_invoice, date_format)
            date_due = datetime.strptime(inv.date_due, date_format)
            res = (date_due - date_invoice).days
        return res

    @api.multi
    def get_email_template(self):
        if self.type == 'out_invoice':
            template = self.env.ref(
                'l10n_ec_sri_ece.email_template_factura_electronica', False)
        elif self.type == 'in_invoice':
            template = self.env.ref(
                'l10n_ec_sri_ece.email_template_retencion_electronica', False)
        elif self.type == 'out_refund':
            template = self.env.ref(
                'l10n_ec_sri_ece.email_template_nota_de_credito_electronica', False)
        return template

    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
           message loaded by default
        """
        if self.tipoem == 'E':
            self.ensure_one()

            # Seleccionamos la plantilla de acuerdo al tipo.
            template = self.get_email_template()

            compose_form = self.env.ref(
                'mail.email_compose_message_wizard_form', False)
            ctx = dict(
                default_model='account.invoice',
                default_res_id=self.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode='comment',
                mark_invoice_as_sent=True,
            )
            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }
        else:
            return super(AccountInvoice, self).action_invoice_sent()

    def emision_documentos_electronicos(self, aut, tipo):
        if aut.tipoem != 'E':
            return
        if tipo == 'f':
            if self.factura_electronica_id:
                if self.factura_electronica_id.estado in ('RECIBIDA', 'AUTORIZADO'):
                    return
            self.button_send_factura_electronica()
        elif tipo == 'r':
            if self.retencion_electronica_id:
                if self.retencion_electronica_id.estado in ('RECIBIDA', 'AUTORIZADO'):
                    return
            self.button_send_retencion_electronica()
        elif tipo == 'nc':
            if self.nota_credito_electronica_id:
                if self.nota_credito_electronica_id.estado in ('RECIBIDA', 'AUTORIZADO'):
                    return
            self.button_send_nota_credito_electronica()
        return

    @api.multi
    def button_corregir_documentos_electronicos(self):
        if self.tipoem != 'E':
            return
        if self.type == 'out_invoice':
            if self.factura_electronica_id:
                if self.factura_electronica_id.estado not in ('RECIBIDA', 'AUTORIZADO'):
                    edoc = self.factura_electronica_id
                    self.factura_electronica_id = False
                    self.button_send_factura_electronica()
        if self.type == 'in_invoice':
            if self.retencion_electronica_id:
                if self.retencion_electronica_id.estado not in ('RECIBIDA', 'AUTORIZADO'):
                    edoc = self.retencion_electronica_id
                    self.retencion_electronica_id = False
                    self.button_send_retencion_electronica()
        elif self.type == 'out_refund':
            if self.nota_credito_electronica_id:
                if self.nota_credito_electronica_id.estado not in ('RECIBIDA', 'AUTORIZADO'):
                    edoc = self.nota_credito_electronica_id
                    self.nota_credito_electronica_id = False
                    self.button_send_nota_credito_electronica()

        queue = self.env.ref('l10n_ec_sri_ece.documento_electronico_queue')

        queue_line = queue.queue_line_ids.filtered(
            lambda x: x.documento_electronico_id == edoc
            )

        edoc.unlink()
        if queue_line:
            queue_line.unlink()
        return


    @api.multi
    def get_infoadicional(self):
        """
        Información adicional para las notas de crédito
        y facturas.
        return: [(nombre,valor),(nombre,valor)]
        """
        return []

    @api.multi
    def get_infotributaria_dict(
            self, ambiente_id, tipoemision, company, ruc,
            claveacceso, comprobante, establecimiento,
            puntoemision, secuencial):

        infoTributaria = OrderedDict([
            ('ambiente', ambiente_id.ambiente),
            ('tipoEmision', tipoemision),
            ('razonSocial', self.normalize_text(company.name)),
            ('nombreComercial', self.normalize_text(
                company.partner_id.tradename or company.name)),
            ('ruc', ruc),
            ('claveAcceso', claveacceso),
            ('codDoc', comprobante),
            ('estab', establecimiento),
            ('ptoEmi', puntoemision),
            ('secuencial', secuencial),
            ('dirMatriz', self.normalize_text(
                company.street or company.street + company.street2)),
        ])

        return infoTributaria

    def normalize_date(self, date):
        if not date:
            return
        try:
            res = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            res = datetime.strptime(
                date, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
        return res

    # FACTURA ELECTRÓNICA
    factura_electronica_id = fields.Many2one(
        'l10n_ec_sri.documento.electronico', ondelete='restrict',
        string="Factura electrónica", copy=False, )

    @api.multi
    def get_propina(self):
        """
        Modificar con super
        :param self:
        :return: propina float
        """
        propina = 0.00
        return propina

    @api.multi
    def get_factura_dict(self):
        """
        :return:
         ambiente_id: en recordset,
         factura: OrderedDict,
         claveacceso: string,
         tipoemision: string,
        """
        ambiente_id = self.env.user.company_id.ambiente_id
        company = self.env.user.company_id
        company_fiscal = company.partner_id.property_account_position_id
        ruc = company.vat

        if ambiente_id.ambiente == '1':
            # Si el ambiente es de pruebas enviamos siempre la fecha actual.
            fechaemision = fields.Date.context_today(self)
        else:
            fechaemision = self.date_invoice
        fechaemision = datetime.strptime(fechaemision, "%Y-%m-%d")
        fechaemision = pytz.timezone(u'America/Guayaquil').localize(fechaemision, is_dst=None)
        fechaemision = fields.Date.to_string(fechaemision)

        autorizacion_id = self.autorizacion_id
        comprobante_id = self.comprobante_id
        comprobante = comprobante_id.code
        establecimiento = self.establecimiento
        puntoemision = self.puntoemision
        tipoemision = '1'  # offline siempre es normal.
        secuencial = self.secuencial.zfill(9)
        partner = self.partner_id
        fiscal = partner.property_account_position_id
        de_obj = self.env['l10n_ec_sri.documento.electronico']

        if self.autorizacion:
            claveacceso = self.autorizacion
        else:
            claveacceso = de_obj.get_claveacceso(
                fechaemision, comprobante, ruc, ambiente_id,
                establecimiento, puntoemision, secuencial)

        infoTributaria = self.get_infotributaria_dict(
            ambiente_id, tipoemision, company, ruc,
            claveacceso, comprobante, establecimiento,
            puntoemision, secuencial)

        totalConImpuestos = OrderedDict([
            ('totalImpuesto', []),
        ])

        for tax in self.sri_tax_line_ids:
            if tax.group in ('ImpGrav', 'Imponible', 'NoGraIva', 'ImpExe', 'Ice', 'Irbpnr'):
                totalConImpuestos['totalImpuesto'].append(
                    OrderedDict([
                        ('codigo', tax.codigo),
                        ('codigoPorcentaje', tax.codigoporcentaje),
                        ('descuentoAdicional', '{:.2f}'.format(0)),  # TODO
                        ('baseImponible', '{:.2f}'.format(tax.base)),
                        ('valor', '{:.2f}'.format(abs(tax.amount))),
                    ])
                )

        pagos = OrderedDict([
            ('pago', []),
        ])

        for p in self.payment_ids:
            pagos['pago'].append(
                OrderedDict([
                    ('formaPago', p.formapago_id.code),
                    ('total', '{:.2f}'.format(p.amount)),
                    ('plazo', 30),  # TODO
                    ('unidadTiempo', 'dias'),  # TODO
                ]))

        if sum(self.payment_ids.mapped('amount')) < self.amount_total:
            pagos['pago'].append(
                OrderedDict([
                    ('formaPago', partner.formapago_id.code or '01'),
                    ('total', '{:.2f}'.format(self.amount_total -
                                              sum(self.payment_ids.mapped('amount')))),
                    ('plazo', 30),  # TODO
                    ('unidadTiempo', 'dias'),  # TODO
                ])
            )

        infoFactura = OrderedDict([
            ('fechaEmision', self.normalize_date(fechaemision)),
            ('dirEstablecimiento', self.normalize_text(
                autorizacion_id.direstablecimiento or company.street or company.street + company.street2)),
            ('contribuyenteEspecial', company.contribuyenteespecial or '000'),
            ('obligadoContabilidad',
             company_fiscal.obligada_contabilidad and 'SI' or 'NO'),
            ('tipoIdentificacionComprador',
             fiscal.identificacion_id.tpidcliente),
            ('guiaRemision', '000-000-000000000'),  # TODO
            ('razonSocialComprador', self.normalize_text(partner.name)),
            ('identificacionComprador', partner.vat),
            ('direccionComprador', self.normalize_text(partner.street)),
            ('totalSinImpuestos', '{:.2f}'.format(self.amount_untaxed)),
            ('totalDescuento', '{:.2f}'.format(self.price_discount)),
            ('totalConImpuestos', totalConImpuestos),
            ('propina', '{:.2f}'.format(self.get_propina())),
            ('importeTotal', '{:.2f}'.format(self.total)),
            ('moneda', 'DOLAR'),
            ('pagos', pagos),
        ])

        detalles = OrderedDict([
            ('detalle', []),
        ])

        for line in self.invoice_line_ids:
            impuestos = OrderedDict([
                ('impuesto', []),
            ])

            for tax in line.sri_tax_line_ids:
                if tax.group in ('ImpGrav', 'Imponible', 'NoGraIva', 'ImpExe', 'Ice', 'Irbpnr'):
                    impuestos['impuesto'].append(
                        OrderedDict([
                            ('codigo', tax.codigo),
                            ('codigoPorcentaje', tax.codigoporcentaje),
                            ('tarifa', tax.porcentaje),
                            ('baseImponible', '{:.2f}'.format(tax.base)),
                            ('valor', '{:.2f}'.format(abs(tax.amount))),
                        ])
                    )

            detalle = OrderedDict([
                ('codigoPrincipal', self.normalize_text(line.product_id.default_code or 'NA')),
                ('codigoAuxiliar', self.normalize_text(line.product_id.barcode or 'NA')),
                ('descripcion', self.normalize_text(line.name)[0:299]),
                ('cantidad', '{:.6f}'.format(line.quantity)),
                ('precioUnitario', '{:.6f}'.format(line.price_unit)),
                ('descuento', '{:.2f}'.format(line.price_discount)),
                ('precioTotalSinImpuesto',
                 '{:.2f}'.format(line.price_subtotal)),
            ])

            detAdicionales = line.get_detallesadicionales()

            if detAdicionales:
                detallesAdicionales = OrderedDict([
                    ('detAdicional', []),
                ])
                for d in detAdicionales:
                    detallesAdicionales['detAdicional'].append(OrderedDict([
                        ('@nombre', self.normalize_text(d[0])),
                        ('@valor', self.normalize_text(d[1])),
                    ]))
                detalle.update(
                    OrderedDict([
                        ('detallesAdicionales', detallesAdicionales),
                    ])
                )

            detalle.update(
                OrderedDict([
                    ('impuestos', impuestos),
                ])
            )

            detalles['detalle'].append(detalle)

            factura_dict = OrderedDict([
                ('factura', OrderedDict([
                    ('@id', 'comprobante'),
                    ('@version', '1.1.0'),
                    ('infoTributaria', infoTributaria),
                    ('infoFactura', infoFactura),
                    ('detalles', detalles),
                ]),
                )
            ])

        camposAdicionales = self.get_infoadicional()
        if camposAdicionales:
            infoAdicional = OrderedDict([
                ('campoAdicional', []),
            ])
            for c in camposAdicionales:
                infoAdicional['campoAdicional'].append(OrderedDict([
                    ('@nombre', self.normalize_text(c[0])),
                    ('#text', self.normalize_text(c[1])),
                ]))

            factura_dict.get('factura').update(OrderedDict([
                ('infoAdicional', infoAdicional),
            ])
            )

        return ambiente_id, comprobante_id, factura_dict, claveacceso, tipoemision

    @api.multi
    def button_send_factura_electronica(self):
        ambiente_id, comprobante_id, factura, claveacceso, tipoemision = self.get_factura_dict()
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        reference = 'account.invoice,%s' % self.id
        vals = de_obj.get_documento_electronico_dict(
            ambiente_id, comprobante_id, factura, claveacceso, tipoemision, reference
        )
        # La autorizacion de la factura es igual a la clave de acceso.
        self.autorizacion = claveacceso

        if self.factura_electronica_id:
            self.factura_electronica_id.write(vals)
        else:
            de = de_obj.create(vals)
            self.factura_electronica_id = de

        # Envía la nc y el archivo xml electónico a los correos de los clientes.
        # self.send_email_de()
        return True

    # RETENCIÓN ELECTRÓNICA.
    retencion_electronica_id = fields.Many2one(
        'l10n_ec_sri.documento.electronico', ondelete='restrict',
        string="Retención electronica", copy=False, )

    @api.multi
    def get_retencion_dict(self):
        """
        En caso de requerirse el tag infoAdicional se debe agregar con un super.

        :return:
         ambiente_id: en recordset,
         comprobanteRetencion: OrderedDict,
         claveacceso: string,
         tipoemision: string,
        """
        ambiente_id = self.env.user.company_id.ambiente_id
        company = self.env.user.company_id
        company_fiscal = company.partner_id.property_account_position_id
        ruc = company.vat

        if ambiente_id.ambiente == '1':
            # Si el ambiente es de pruebas enviamos siempre la fecha actual.
            fechaemision = fields.Date.context_today(self)
        else:
            fechaemision = self.fechaemiret1
        fechaemision = datetime.strptime(fechaemision, "%Y-%m-%d")
        fechaemision = pytz.timezone(u'America/Guayaquil').localize(fechaemision, is_dst=None)
        fechaemision = fields.Date.to_string(fechaemision)

        autorizacion_id = self.r_autorizacion_id
        comprobante_id = self.r_comprobante_id
        comprobante = comprobante_id.code
        establecimiento = self.estabretencion1
        puntoemision = self.ptoemiretencion1
        tipoemision = '1'  # offline siempre es normal.
        secuencial = self.secretencion1.zfill(9)

        # Se refiere al documento del proveedor.
        if not self.establecimiento \
            or not self.puntoemision \
            or not self.establecimiento:
            raise UserError(_(
                u"Debe ingresar el secuencial, punto de emisión y " \
                u"establecimiento del comprobante de compra"
            ))
        numdocsustento = ''.join([
            self.establecimiento.zfill(3),
            self.puntoemision.zfill(3),
            self.secuencial.zfill(9)
        ])

        partner = self.partner_id
        fiscal = partner.property_account_position_id
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        if self.autretencion1:
            claveacceso = self.autretencion1
        else:
            claveacceso = de_obj.get_claveacceso(
                fechaemision, comprobante, ruc, ambiente_id,
                establecimiento, puntoemision, secuencial)

        infoTributaria = self.get_infotributaria_dict(
            ambiente_id, tipoemision, company, ruc,
            claveacceso, comprobante, establecimiento,
            puntoemision, secuencial)

        infoCompRetencion = OrderedDict([
            ('fechaEmision', self.normalize_date(fechaemision)),
            ('dirEstablecimiento', self.normalize_text(
                autorizacion_id.direstablecimiento or company.street + company.street2)),
            ('contribuyenteEspecial', company.contribuyenteespecial or '000'),
            ('obligadoContabilidad',
             company_fiscal.obligada_contabilidad and 'SI' or 'NO'),
            ('tipoIdentificacionSujetoRetenido',
             fiscal.identificacion_id.tpidcliente),
            ('razonSocialSujetoRetenido', self.normalize_text(partner.name)),
            ('identificacionSujetoRetenido', partner.vat),
            ('periodoFiscal', self.normalize_date(fechaemision)[3:10]),
        ])

        impuestos = OrderedDict([
            ('impuesto', []),
        ])

        for i in self.sri_tax_line_ids.filtered(lambda l: l.group in (
            'RetAir', 'RetBien10', 'RetServ20', 'RetServ50', 'RetBienes',
                'RetServicios', 'RetServ100')):
            impuestos['impuesto'].append(
                OrderedDict([
                    ('codigo', i.codigo),
                    ('codigoRetencion', i.codigoporcentaje),
                    ('baseImponible', i.base),
                    ('porcentajeRetener', i.porcentaje),
                    ('valorRetenido', '{:.2f}'.format(i.amount)),
                    ('codDocSustento', self.comprobante_id.code),
                    ('numDocSustento', numdocsustento),
                    ('fechaEmisionDocSustento',
                     self.normalize_date(self.date_invoice)),
                ]))

        retencion_dict = OrderedDict([
            ('comprobanteRetencion', OrderedDict([
                ('@id', 'comprobante'),
                ('@version', '1.0.0'),
                ('infoTributaria', infoTributaria),
                ('infoCompRetencion', infoCompRetencion),
                ('impuestos', impuestos),
            ]),
            )
        ])
        return ambiente_id, comprobante_id, retencion_dict, claveacceso, tipoemision

    @api.multi
    def button_send_retencion_electronica(self):
        ambiente_id, comprobante_id, retencion_dict, claveacceso, tipoemision = self.get_retencion_dict()
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        reference = 'account.invoice,%s' % self.id
        vals = de_obj.get_documento_electronico_dict(
            ambiente_id, comprobante_id, retencion_dict, claveacceso, tipoemision, reference
        )
        # La autorizacion de la retencion es igual a la clave de acceso.
        self.autretencion1 = claveacceso

        if self.retencion_electronica_id:
            self.retencion_electronica_id.write(vals)
        else:
            de = de_obj.create(vals)
            self.retencion_electronica_id = de

        # self.send_email_de()

        return True

    @api.multi
    def send_de_backend(self):
        edoc = self.factura_electronica_id or self.retencion_electronica_id or self.nota_credito_electronica_id
        if edoc:
            edoc.process_de()
        return True

    @api.multi
    @api.depends(
        'factura_electronica_id.estado',
        'retencion_electronica_id.estado',
        'nota_credito_electronica_id.estado')
    def _get_ce_state(self):
        for r in self:
            edoc = r.factura_electronica_id or r.retencion_electronica_id or r.nota_credito_electronica_id
            if edoc:
                r.ce_state = edoc.estado
            return True

    ce_state = fields.Char('CE State', store=True, compute=_get_ce_state)

    @api.multi
    def send_email_de(self):
        self.ensure_one()
        template = self.get_email_template()
        template.send_mail(self.ids[0], force_send=True)
        return True

    # NOTA DE CRÉDITO ELECTRÓNICA.
    nota_credito_electronica_id = fields.Many2one(
        'l10n_ec_sri.documento.electronico', ondelete='restrict',
        string="Nota de crédito electronica", copy=False, )

    @api.multi
    def get_nota_credito_dict(self):
        """
        :return:
         ambiente_id: en recordset,
         nota_credito_dict: OrderedDict,
         claveacceso: string,
         tipoemision: string,
        """
        ambiente_id = self.env.user.company_id.ambiente_id
        company = self.env.user.company_id
        company_fiscal = company.partner_id.property_account_position_id
        ruc = company.vat
        if ambiente_id.ambiente == '1':
            # Si el ambiente es de pruebas enviamos siempre la fecha actual.
            fechaemision = fields.Date.context_today(self)
        else:
            fechaemision = self.date_invoice
        fechaemision = datetime.strptime(fechaemision, "%Y-%m-%d")
        fechaemision = pytz.timezone(u'America/Guayaquil').localize(fechaemision, is_dst=None)
        fechaemision = fields.Date.to_string(fechaemision)

        autorizacion_id = self.autorizacion_id
        comprobante_id = self.comprobante_id
        comprobante = comprobante_id.code
        establecimiento = self.establecimiento
        puntoemision = self.puntoemision
        tipoemision = '1'  # offline siempre es normal.
        secuencial = self.secuencial.zfill(9)
        numdocsustento = establecimiento + puntoemision + secuencial
        partner = self.partner_id
        fiscal = partner.property_account_position_id
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        if self.autorizacion:
            claveacceso = self.autorizacion
        else:
            claveacceso = de_obj.get_claveacceso(
                fechaemision, comprobante, ruc, ambiente_id,
                establecimiento, puntoemision, secuencial)

        docmodificado = self.origin_invoice_ids
        numdocmodificado = '-'.join([
            docmodificado.establecimiento,
            docmodificado.puntoemision,
            docmodificado.secuencial.zfill(9)
        ])

        if len(docmodificado) != 1:
            raise UserError(_("Debe tener un documento modificado."))

        infoTributaria = self.get_infotributaria_dict(
            ambiente_id, tipoemision, company, ruc,
            claveacceso, comprobante, establecimiento,
            puntoemision, secuencial)

        totalConImpuestos = OrderedDict([
            ('totalImpuesto', []),
        ])

        for i in self.sri_tax_line_ids.filtered(lambda l: l.group in (
                'ImpGrav', 'Imponible', 'NoGraIva', 'ImpExe', 'Ice', 'Irbpnr')):
            totalConImpuestos['totalImpuesto'].append(
                OrderedDict([
                    ('codigo', i.codigo),
                    ('codigoPorcentaje', i.codigoporcentaje),
                    ('baseImponible', i.base),
                    ('valor', '{:.2f}'.format(i.amount)),
                ])
            )

        infoNotaCredito = OrderedDict([
            ('fechaEmision', self.normalize_date(fechaemision)),
            ('dirEstablecimiento', self.normalize_text(
                autorizacion_id.direstablecimiento or company.street + company.street2)),
            ('tipoIdentificacionComprador', fiscal.identificacion_id.tpidcliente),
            ('razonSocialComprador', self.normalize_text(partner.name)),
            ('identificacionComprador', partner.vat),
            ('contribuyenteEspecial', company.contribuyenteespecial or '000'),
            ('obligadoContabilidad',
             company_fiscal.obligada_contabilidad and 'SI' or 'NO'),
            # ('rise', "TODO",
            ('codDocModificado', docmodificado.comprobante_id.code),
            ('numDocModificado', numdocmodificado),
            ('fechaEmisionDocSustento', self.normalize_date(
                docmodificado.date_invoice)),
            ('totalSinImpuestos', self.subtotal),
            ('valorModificacion', self.total),
            ('moneda', self.currency_id.name),
            ('totalConImpuestos', totalConImpuestos),
            ('motivo', self.name),
        ])

        detalles = OrderedDict([
            ('detalle', []),
        ])

        for line in self.invoice_line_ids:
            impuestos = OrderedDict([
                ('impuesto', []),
            ])

            for tax in line.sri_tax_line_ids:
                if tax.group in ('ImpGrav', 'Imponible', 'NoGraIva', 'ImpExe', 'Ice', 'Irbpnr'):
                    impuestos['impuesto'].append(
                        OrderedDict([
                            ('codigo', tax.codigo),
                            ('codigoPorcentaje', tax.codigoporcentaje),
                            ('tarifa', tax.porcentaje),
                            ('baseImponible', '{:.2f}'.format(tax.base)),
                            ('valor', '{:.2f}'.format(abs(tax.amount))),
                        ])
                    )

            detalle = OrderedDict([
                ('codigoInterno', self.normalize_text(line.product_id.default_code or 'NA')),
                ('codigoAdicional', self.normalize_text(line.product_id.barcode or 'NA')),
                ('descripcion', self.normalize_text(line.name)[0:299]),
                ('cantidad', '{:.6f}'.format(line.quantity)),
                ('precioUnitario', '{:.6f}'.format(line.price_unit)),
                ('descuento', '{:.2f}'.format(line.price_discount)),
                ('precioTotalSinImpuesto',
                 '{:.2f}'.format(line.price_subtotal)),
            ])

            detAdicionales = line.get_detallesadicionales()

            if detAdicionales:
                detallesAdicionales = OrderedDict([
                    ('detAdicional', []),
                ])
                for d in detAdicionales:
                    detallesAdicionales['detAdicional'].append(OrderedDict([
                        ('@nombre', self.normalize_text(d[0])),
                        ('@valor', self.normalize_text(d[1])),
                    ]))
                detalle.update(
                    OrderedDict([
                        ('detallesAdicionales', detallesAdicionales),
                    ])
                )

            detalle.update(
                OrderedDict([
                    ('impuestos', impuestos),
                ])
            )

            detalles['detalle'].append(detalle)

        nota_credito_dict = OrderedDict([
            ('notaCredito', OrderedDict([
                ('@id', 'comprobante'),
                ('@version', '1.1.0'),
                ('infoTributaria', infoTributaria),
                ('infoNotaCredito', infoNotaCredito),
                ('detalles', detalles),
            ])
            )
        ])

        camposAdicionales = self.get_infoadicional()
        if camposAdicionales:
            infoAdicional = OrderedDict([
                ('campoAdicional', []),
            ])
            for c in camposAdicionales:
                infoAdicional['campoAdicional'].append(OrderedDict([
                    ('@nombre', self.normalize_text(i[0])),
                    ('#text', self.normalize_text(i[1])),
                ]))

            nota_credito_dict.get('notaCredito').update(OrderedDict([
                ('infoAdicional', infoAdicional),
            ])
            )

        return ambiente_id, comprobante_id, nota_credito_dict, claveacceso, tipoemision

    @api.multi
    def button_send_nota_credito_electronica(self):
        ambiente_id, comprobante_id, nota_credito, claveacceso, tipoemision = self.get_nota_credito_dict()
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        reference = 'account.invoice,%s' % self.id
        vals = de_obj.get_documento_electronico_dict(
            ambiente_id, comprobante_id, nota_credito, claveacceso, tipoemision, reference
        )
        # La autorizacion de la factura es igual a la clave de acceso.
        self.autorizacion = claveacceso

        if self.nota_credito_electronica_id:
            self.nota_credito_electronica_id.write(vals)
        else:
            de = de_obj.create(vals)
            self.nota_credito_electronica_id = de

        # Envía la nc y el archivo xml electónico a los correos de los clientes.
        # self.send_email_de()

        return True

