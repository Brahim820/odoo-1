# -*- coding: utf-8 -*-
import base64
from cStringIO import StringIO as s
import zipfile
import xmltodict

from openerp import models, fields, api, _
from openerp.exceptions import UserError
from datetime import datetime

class CustomPopMessage(models.TransientModel):
    _name = "custom.pop.message"
    _description = "Registers advices with the operations of electronic documents."
    
    name = fields.Text('Mensaje', readonly=True)
    
    def messagebox(self,advices):
        return {
            'name': 'Odoo - Aviso',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom.pop.message',
                'target':'new',
                'context':{'default_name': advices} 
                }

class ComprobanteElectronicoImportWizardLine(models.TransientModel):
    _name = "l10n_ec_sri.ce.import.wizard.line"
    _description = "Register multiple SRI information on invoices."

    import_file = fields.Binary('File:', )
    wizard_id = fields.Many2one(
        'l10n_ec_sri.ce.import.wizard', string="Wizard", )


class ComprobanteElectronicoImportWizard(models.TransientModel):
    _name = "l10n_ec_sri.ce.import.wizard"
    _description = "Register multiple SRI information on invoices."

    import_file = fields.Binary('File:', )
    wizard_line_ids = fields.One2many(
        'l10n_ec_sri.ce.import.wizard.line', inverse_name='wizard_id',
        string='Wizard lines', )

    @api.multi
    def get_de_dict(
            self, estado, xml, infotributaria):
        """
        :param estado:
        :param xml:
        :param infotributaria:
        :return:
        """
        comprobante = self.env['l10n_ec_sri.comprobante'].search(
            [('code', '=', infotributaria['codDoc'])], limit=1)

        context, active_model, active_id = self.params_context()
        
        if active_id and active_model:
            vals = {
                'xml_file': xml,
                'xml_filename': infotributaria['claveAcceso'] + '.xml',
                'estado': estado,
                # 'mensajes': envio['comprobantes'] or '',
                'ambiente': infotributaria['ambiente'],
                'tipoemision': infotributaria['tipoEmision'],
                'claveacceso': infotributaria['claveAcceso'],
                'reference': ('{0},{1}'.format(active_model, active_id[0])), #TODO
                'comprobante_id': comprobante.id,
            }
        else:
            vals = {
                'xml_file': xml,
                'xml_filename': infotributaria['claveAcceso'] + '.xml',
                'estado': estado,
                # 'mensajes': envio['comprobantes'] or '',
                'ambiente': infotributaria['ambiente'],
                'tipoemision': infotributaria['tipoEmision'],
                'claveacceso': infotributaria['claveAcceso'],
                'comprobante_id': comprobante.id,
            }
        return vals

    @api.multi
    def normalize_date_to_odoo(self, date):
        if not date:
            return
        res = datetime.strptime(date, '%d/%m/%Y').strftime( '%Y-%m-%d')
        return res

    @api.multi
    def get_de_from_xml(self, xml):
        """
        :param xml:
        :return:
        """
        autorizacion_dict = xmltodict.parse(xml)['autorizacion']
        estado = autorizacion_dict['estado']

        comprobante = autorizacion_dict['comprobante'].encode('utf-8')
        comprobante = xmltodict.parse(comprobante)

        inv_obj = self.env['account.invoice']

        if 'factura' in comprobante.keys():
            infoTributaria = comprobante['factura']['infoTributaria']
            infoFactura = comprobante['factura']['infoFactura']
            key = 'factura'           
            
            fecha = infoFactura['fechaEmision'] 
            vat = infoFactura['identificacionComprador']
            partner = self.env['res.partner'].search([('vat', '=', vat)], limit=1)
            
            if not partner:      #TODO No crea aun los usuarios falta corregir
                partner = self.env['res.partner']
                partner.create({
                    'name': infoFactura['razonSocialComprador'],
                    'vat': vat,
                    'street': infoFactura['direccionComprador']
                    })
                          
            detalle = comprobante['factura']['detalles']['detalle'] 
                                   
            supplier = self.env['product.supplierinfo']
            supplier = supplier.search([('name', '=', partner.id)])

            inv = inv_obj.search([('secuencial', '=', infoTributaria['secuencial'])])
            
            secuencial = infoTributaria['secuencial']
                             
            lines = []           
            if supplier:
                for d in detalle:
                              
                    d_supplier = supplier.filtered(
                        lambda x: x.product_code == d['codigoPrincipal'] or 
                        x.product_name == d['descripcion'] or 
                        x.product_name in d['descripcion'] or 
                        d['descripcion'] in x.product_name)
                                                         
                    product = d_supplier.product_tmpl_id
                    
                    if partner.property_account_position_id and product.supplier_taxes_id:
                        tax_ids = partner.property_account_position_id.map_tax(product.supplier_taxes_id).ids
                    else:
                        tax_ids = product.supplier_taxes_id.ids
                                   
                    account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id 
      
                    lines.append((0,0, {
                        'product_id': d_supplier.product_tmpl_id.id,
                        'quantity': d['cantidad'],
                        'price_unit': d['precioUnitario'],
                        'name':  d['descripcion'], 
                        'account_id': account.id, 
                        'invoice_line_tax_ids': [(6, 0, tax_ids)],
                        }))
            else:
                products = self.env['product.product']
                for d in detalle:                                                               
                    product = products.search(
                        [('default_code','=', d['codigoPrincipal'])])
                    if not product:
                        product = products.search([('name','=',d['descripcion'])])
                                                                                                                
                    if partner.property_account_position_id and product.supplier_taxes_id:
                        tax_ids = partner.property_account_position_id.map_tax(product.supplier_taxes_id).ids
                    else:
                        tax_ids = product.supplier_taxes_id.ids
                                                            
                    account = product.property_account_expense_id or product.categ_id.property_account_expense_categ_id 
       
                    lines.append((0,0, {
                        'product_id': product.product_tmpl_id.id,
                        'quantity': d['cantidad'],
                        'price_unit': d['precioUnitario'],
                        'name':  d['descripcion'], 
                        'account_id': account.id, 
                        'invoice_line_tax_ids': [(6, 0, tax_ids)],
                        }))
                
                
            inv_dict = {
                'comprobante_id': self.env['l10n_ec_sri.comprobante'].search(
                 [('code', '=', infoTributaria['codDoc'])], limit=1).id,
                'secuencial': infoTributaria['secuencial'],
                'partner_id': partner.id,
                'date_invoice': self.normalize_date_to_odoo(fecha),
                'invoice_line_ids': lines,
                'establecimiento': infoTributaria['estab'],
                'puntoemision': infoTributaria['ptoEmi'],
                'autorizacion': autorizacion_dict['numeroAutorizacion'],                
                }
            
        elif 'comprobanteRetencion' in comprobante.keys():
            infoTributaria = comprobante['comprobanteRetencion']['infoTributaria']
            key = 'comprobanteRetencion'
            fecha = comprobante['comprobanteRetencion']['infoCompRetencion']['fechaEmision']
            
            inv_obj = self.env['account.invoice']
            docs = []
            
            for impuesto in comprobante['comprobanteRetencion']['impuestos']['impuesto']:
                if impuesto['numDocSustento'] not in docs:
                    docs.append(impuesto['numDocSustento'])
                    
            for d in docs:
                establecimiento = d[:3]
                ptoemision = d[3:6]
                secuencial = d[6:].lstrip('+-0')
                inv += inv_obj.search([('establecimiento','=',establecimiento), 
                                     ('puntoemision','=',ptoemision),
                                     ('secuencial','=',secuencial)])

            fecha = comprobante['comprobanteRetencion']['infoCompRetencion']['fechaEmision']
             
            inv_dict = {
                'r_comprobante_id': self.env['l10n_ec_sri.comprobante'].search(
                [('code', '=', infoTributaria['codDoc'])], limit=1).id,
                'fechaemiret1': self.normalize_date_to_odoo(fecha),
                'estabretencion1': infoTributaria['estab'],
                'ptoemiretencion1': infoTributaria['ptoEmi'],
                'autretencion1': autorizacion_dict['numeroAutorizacion'], 
                'secretencion1': infoTributaria['secuencial'],               
                }

        elif 'guiaRemision' in comprobante.keys():
            infoTributaria = comprobante['guiaRemision']['infoTributaria']
            key = 'guiaRemision'
        
        vals = self.get_de_dict(estado, xml, infoTributaria)
        de_obj = self.env['l10n_ec_sri.documento.electronico']
        de = de_obj.create(vals)

        autorizacion = autorizacion_dict['numeroAutorizacion']

        return de, key, infoTributaria, autorizacion, inv_dict, inv, secuencial

    @api.multi
    def _process_file(self, active_model, active_ids, file, list_msg):
        active_records = self.env[active_model].browse(active_ids)
        fileio = s(base64.b64decode(file))
        if zipfile.is_zipfile(fileio):
            with zipfile.ZipFile(fileio, 'r') as zip_file:
                members = zipfile.ZipFile.namelist(zip_file)
                xml_members = [m for m in members if ".xml" in m]
                if not xml_members:
                    raise UserError(_("Error: Ingrese un archivo xml o zip valido.")) 
                for m in xml_members:
                    xml = zip_file.open(m).read()
                    self.register_de_data(xml, active_model, active_records, list_msg)                                                            
        else: 
            
            xml = base64.b64decode(file)           
            if '<?xml' in xml[:10] :
                self.register_de_data(xml, active_model, active_records, list_msg)
            else:
                raise UserError(_("Error: Ingrese un archivo xml o zip valido."))

    @api.multi
    def register_de_data(self, xml, active_model, active_records, list_msg):
        de, key, info, autorizacion, xml_data, ces, secuencial = self.get_de_from_xml(xml)
        
        for ce in ces:
            creando = False
            if key == 'factura' and active_model == 'account.invoice':
                old_des = active_records.mapped('factura_electronica_id')
                if active_records and not ce and not active_records.invoice_line_ids:
                    active_records.write({
                        'factura_electronica_id': de.id,
                    })
                    active_records.write(xml_data)       
                elif active_records and not ce and  active_records.invoice_line_ids:
                    creando = True
                    new_inv = self.env['account.invoice'].create(xml_data)  
                    new_inv.write({
                         'factura_electronica_id': de.id,
                    })
                    de = de.write({
                        'reference': ('{0},{1}'.format(active_model, new_inv.id))
                        })           
                elif active_records and active_records == ce and not ce.invoice_line_ids:
                    active_records.write({
                        'factura_electronica_id': de.id,
                    })
                    active_records.write(xml_data)
                elif active_records and active_records == ce and ce.invoice_line_ids:
                    creando = True
                    list_msg.append('Ya existe la factura importada con el secuencial %s' % xml_data['secuencial'])
                elif active_records != ce and ce and not ce.invoice_line_ids:
                    active_records = ce   #TODO
                    active_records.write({
                         'factura_electronica_id': de.id,
                     })
                    active_records.write(xml_data)
                elif active_records != ce and ce and ce.invoice_line_ids:
                    creando = True
                    list_msg.append('Ya existe la factura importada con el secuencial %s' % xml_data['secuencial'])
                else:
                    creando = True
                    new_inv = self.env['account.invoice'].create(xml_data)  
                    new_inv.write({
                         'factura_electronica_id': de.id,
                    })
                    de = de.write({
                        'reference': ('{0},{1}'.format(active_model, new_inv.id))
                        })   

            if key == 'comprobanteRetencion' and active_model == 'account.invoice':
                old_des = active_records.mapped('retencion_electronica_id')
                if active_records == ce and ce and not active_records.retencion_electronica_id:
                    active_records.write({
                        'retencion_electronica_id': de.id,
                    })
                    active_records.write(xml_data)
                elif active_records == ce and ce and active_records.retencion_electronica_id:
                    creando = True
                    list_msg.append("Ya existe la retencion ingresada {0} en la factura con el secuencial {1}".format(xml_data['secretencion1'], ce.secuencial))
                elif active_records != ce and ce and not ce.retencion_electronica_id:
                    creando = True
                    active_records = ce
                    active_records.write({
                        'retencion_electronica_id': de.id,
                    })
                    active_records.write(xml_data)
                elif active_records != ce and ce and ce.retencion_electronica_id:
                    creando = True
                    list_msg.append("Ya existe la retencion ingresada {0} en la factura con el secuencial {1}".format(xml_data['secretencion1'],ce.secuencial))
                elif not ce:
                    creando = True
                    list_msg.append("No existe la factura {0} asociada a la retencion ingresada con el secuencial {1}".format(secuencial, xml_data['secretencion1']))
                
            if key == 'guiaRemision' and active_model == 'stock.picking':
                old_des = active_records.mapped('guia_remision_electronica_id').unlink()
                active_records.write({
                    'guia_remision_electronica_id': de.id,
                    'establecimiento': info['estab'],
                    'puntoemision': info['ptoEmi'],
                    'autorizacion': autorizacion,
                    'secuencial': info['secuencial'],
                    # 'min_date': '', TODO?
                })
            # Borramos los documentos antiguos pues está restringido para borrar.
            if not creando:
                old_des.unlink()
    
    def params_context(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        return context, active_model, active_ids    

    @api.multi
    def button_import_file(self):     
        context, active_model, active_ids = self.params_context()

        if not active_model or not active_ids:
            active_model = 'account.invoice'
            active_ids = []
        elif len(active_ids) > 1:
            raise UserError(_("Debe seleccionar solo un registro."))

        for file in self.wizard_line_ids.mapped('import_file'):
            self._process_file(active_model, active_ids, file, list_msg)
            
        msg_obj = self.env['custom.pop.message'] 
        advices = ''
        list_msg = list(set(list_msg))
        if list_msg:
            for msg in list_msg:
                advices += msg+'\n'      
            return msg_obj.messagebox(advices)
        