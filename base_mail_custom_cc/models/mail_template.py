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
        The function _get_custom_email_cc must be implemented on the model
        you need to get the cc from, it should return a list of ids:

        def _get_custom_email_cc(self, template=False)
            do_something
            return [1,2,3]

        """
        r = super(MailTemplate, self).generate_email(res_ids, fields=fields)

        try:
            cc = self.env[r[res_ids[0]]['model']].browse(
                r[res_ids[0]]['res_id'])._get_custom_email_cc(template=self)
            if cc:
                r[res_ids[0]]['email_cc'] = cc
        except:
            try:
                cc = self.env[r['model']].browse(r['res_id'])._get_custom_email_cc(template=self)
                if cc:
                    r['email_cc'] = cc
            except:
                pass
        return r

