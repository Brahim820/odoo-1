# -*- coding: utf-8 -*-
import base64

from openerp import api, models
from openerp import report as odoo_report
from openerp import tools


class MailTemplate(models.Model):
    _inherit = ['mail.template']

    @api.multi
    def generate_email(self, res_ids, fields=None):
        """
        The function _get_custom_attachment must be implemented on the model
        you need to get attachments from.

        You must return a list of tuples with the name and the content on base64.

        attachments = [('name_with.extension','base64string')]

        """
        r = super(MailTemplate, self).generate_email(res_ids, fields=fields)

        try:
            attachments = self.env[r[res_ids[0]]['model']].browse(
                r[res_ids[0]]['res_id'])._get_custom_attachments(template=self)
            if attachments:
                r[res_ids[0]]['attachments'].extend(attachments)
        except:
            try:
                attachments = self.env[r['model']].browse(r['res_id'])._get_custom_attachments(template=self)
                if attachments:
                    r['attachments'].extend(attachments)
            except:
                pass

        return r

