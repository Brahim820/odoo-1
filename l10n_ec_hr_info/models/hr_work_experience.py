#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openerp import _, api, fields, models


class HrWorkExperience(models.Model):
    """
    Record the employee's work experience
    """
    _name = 'hr.work.experience'
    _description = __doc__

    name = fields.Char(_('Job Position'), required=True)
    employee_id = fields.Many2one('hr.employee', string=_('Employee'))
    company_id = fields.Many2one('hr.work.company', string=_('Company'), required=True)
    exit_reason = fields.Char(_('Exit Reason'))
    date_start = fields.Date(_('Date Start'), required=True)
    date_stop = fields.Date(_('Date Stop'), required=True)
    contact = fields.Char(_('Company Contact'))
    contact_phone = fields.Char(_('Contact Phone'))


class HrWorkCompany(models.Model):
    """
    Register the companies in which the employee has worked
    """
    _name = 'hr.work.company'
    _description = __doc__

    @api.multi
    def onchange_state(self, state_id):
        if state_id:
            state = self.env['res.country.state'].browse(state_id)
            return {'value': {'country_id': state.country_id.id}}
        return {'value': {}}

    name = fields.Char(_('Name of the Institution'), required=True)
    street = fields.Char(_('Street'))
    street2 = fields.Char(_('Street2'))
    zip = fields.Char(_('Zip'), size=24, change_default=True)
    city = fields.Char(_('City'))
    state_id = fields.Many2one('res.country.state', string=_('State'), ondelete='restrict')
    country_id = fields.Many2one('res.country', string=_('Country'), ondelete='restrict')
    email = fields.Char(_('Email'))
    phone = fields.Char(_('Phone'))
    mobile = fields.Char(_('Mobile'))
    website = fields.Char(_('Website'), help="Website of Academic Institution")
