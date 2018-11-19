# -*- coding: utf-8 -*-

import base64
from contextlib import closing
import os
import subprocess
import tempfile
import time

from openerp import models, api, _
from openerp.exceptions import Warning, AccessError, UserError
from openerp.tools.safe_eval import safe_eval
from openerp.tools import config

import logging
_logger = logging.getLogger(__name__)

def _normalize_filepath(path):
    path = path or ''
    path = path.strip()
    path = os.path.normpath(path)
    return path if os.path.exists(path) else False


class Report(models.Model):
    _inherit = 'report'

    def _get_electronic_signatures(self, report=False):
        """
        This is a demo function.
        Implement this function on every model you need to get signatures from.
        return: list of electronic_signature recordsets
        """
        certificates = []

        return certificates

    def _sign_document(self):
        """
        This is a demo function.
        Implement this on every model you need to sign.
        It's important to exclude the report that will not be signed.
        return: True or False
        """
        return False

    def _attach_signed_read(self, docids, filename=False, model=False):
        if len(docids) != 1:
            return False
        if not filename:
            return False
        if not model:
            model = context.get('active_model')
        attachment = self.env['ir.attachment'].search([
            ('datas_fname', '=', filename),
            ('res_model', '=', model),
            ('res_id', '=', docids[0]),
        ], limit=1)
        if attachment:
            return base64.decodestring(attachment.datas)
        return False

    def _attach_signed_write(self, docids, filename=False, signed=False, model=False):
        if len(docids) != 1:
            return False

        if not filename:
            return False
        if not model:
            model = context.get('active_model')
        try:
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.encodestring(signed),
                'datas_fname': filename,
                'res_model': model,
                'res_id': docids[0],
            })
        except AccessError:
            raise UserError(
                _('Saving signed report (PDF): '
                  'You do not have enough access rights to save attachments'))
        return attachment

    def _signer_bin(self, opts):
        me = os.path.dirname(__file__)
        java_bin = 'java -jar'
        jar = '{}/../static/jar/jPdfSign.jar'.format(me)
        return '%s %s %s' % (java_bin, jar, opts)

    @api.multi
    def mass_signature(self, record_id, report):
        form = record_id.read()[0]
        data = {
             'model': str(record_id._model),
             'form': form
            }
        return self.get_pdf([record_id.id], report, html=None, data=data)

    def pdf_sign(self, pdf, certificates):
        pdfsigned = pdf + '.signed.pdf'
        cont = False

        for cert in certificates:
            if not cert.p12:
                raise UserError(_("Certificate: %s has a wrong p12 certificate." % cert.name))
            if not cert.password:
                raise UserError(_("Certificate: %s has an empty password." % cert.name))

            p12 = _normalize_filepath(cert.path)
            data_dir = config['data_dir']
            db = self.env.cr.dbname

            passwd = tempfile.NamedTemporaryFile()
            passwd = tempfile.NamedTemporaryFile(suffix=".txt", prefix="pass_", dir=''.join(
                [data_dir, '/filestore/', db]), delete=False)  # TODO Cambiar la ruta
            try:
                passwd.write(cert.password)
                passwd.seek(0)
                passwd = _normalize_filepath(passwd.name)
            except:
                os.remove(passwd)
                return False

            signer_opts = '"%s" "%s" "%s" "%s"' % (p12, pdf, pdfsigned, passwd)
            signer = self._signer_bin(signer_opts)
            process = subprocess.Popen(
                signer, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = process.communicate()
            os.remove(passwd)
            if process.returncode:
                if 'keystore password was incorrect' in err:
                    raise UserError(
                        _('Incorrect password for certificate: %s.') % cert.name
                    )
                else:
                    raise UserError(
                        _('Signing report (PDF): jPdfSign failed (error code: %s). '
                            'Message: %s. Output: %s') %
                            (process.returncode, err, out)
                    )
            pdf = pdfsigned
            if cont == False:
                pdfsigned = pdfsigned + 'signed.pdf'
                cont = True

        return pdfsigned

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        report = self._get_report_from_name(report_name)
        model = report.model
        model_obj = self.env[model]
        record_ids = model_obj.search([('id','in',docids)])

        signed = ''
        # Only sign one document at a time.
        if len(record_ids) == 1:
            # Check if the document should be signed.
            try:
                sign = record_ids._sign_document(report)
            except:
                sign = False
            if not sign:
                return super(Report, self).get_pdf(
                    record_ids, report_name, html=html, data=data,)

            # Get the certificates for the document.
            try:
                certificates = record_ids._get_electronic_signatures()
            except:
                certificates = []
            if not report.attachment:
                filename = "(object.name or '').replace(' ', '_').lower() + '.signed.pdf'"
                filename = safe_eval(filename, {
                    'object': record_ids,
                    'time': time
                    })
            else:
                filename = self.env['report']._attachment_filename(record_ids, report)
                filename = filename.replace(".pdf", ".signed.pdf")
            signed_content = self._attach_signed_read(docids, filename, model=model)
            if signed_content:
                _logger.debug(
                    "The signed PDF document '%s/%s' was loaded from the "
                    "database", report_name, docids,
                )
                return signed_content
            content = super(Report, self).get_pdf(
                record_ids, report_name, html=html, data=data,
            )
            if certificates:
                # Creating temporary origin PDF
                pdf_fd, pdf = tempfile.mkstemp(
                    suffix='.pdf', prefix='report.tmp.')
                with closing(os.fdopen(pdf_fd, 'w')) as pf:
                    pf.write(content)
                _logger.debug(
                    "Signing PDF document '%s' for IDs %s with certificate '%s'",
                    report_name, docids, certificates,
                )
                signed = self.pdf_sign(pdf, certificates)
                # Read signed PDF
                if os.path.exists(signed):
                    with open(signed, 'rb') as pf:
                        content = pf.read()
                # Manual cleanup of the temporary files
                for fname in (pdf, signed):
                    try:
                        os.unlink(fname)
                    except (OSError, IOError):
                        _logger.error('Error when trying to remove file %s', fname)
                if filename:
                    self._attach_signed_write(docids, filename, content, model=model)
            if signed:
                try:
                    record_ids._complete_sign_process()
                except:
                    pass
            return content
        return super(Report, self).get_pdf(
                record_ids, report_name, html=html, data=data,)

