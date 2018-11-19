# -*- coding: utf-8 -*-
import base64
import tempfile
import os

from openerp import _, api, fields, models
from openerp.exceptions import UserError
from openerp.tools import config

class ElectronicSignature(models.Model):
    _name = 'electronic.signature'

    name = fields.Char(string='Name', required=True, )
    p12 = fields.Binary(string='File', )
    password = fields.Char(string='Password', )
    path = fields.Char(string='Path', )
    valid_to = fields.Date(string='Valid to', )

    def save_sign(self, p12):
        """
        Saves the file to disc
        :param p12: fields.Binary signature pfx
        :return: str() path
        """
        data_dir = config['data_dir']
        db = self.env.cr.dbname
        tmpp12 = tempfile.TemporaryFile()
        tmpp12 = tempfile.NamedTemporaryFile(suffix=".p12", prefix="signature_", dir=''.join(
            [data_dir, '/filestore/', db]), delete=False)
        tmpp12.write(base64.b64decode(p12))
        tmpp12.seek(0)
        return tmpp12.name

    @api.model
    def create(self, vals):
        if 'p12' in vals and vals['p12'] != '':
            vals['path'] = self.save_sign(vals['p12'])
        return super(ElectronicSignature, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'p12' in vals and vals['p12'] != '':
            vals['path'] = self.save_sign(vals['p12'])
        return super(ElectronicSignature, self).write(vals)

    @api.multi
    def unlink(self):
        for r in self:
            if r.path != '':
                os.remove(self.path)
            return super(ElectronicSignature, self).unlink()

    @api.multi
    def button_reset(self):
        for r in self:
            os.remove(r.path)
            r.write({
                'path': '',
                'p12': '',
                'password': '',
            })

