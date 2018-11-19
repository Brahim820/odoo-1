#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, api, fields, models


class HrAcademicTraining(models.Model):
    """
    Managing employees' academic training information
    """
    _name = 'hr.academic.training'
    _description = __doc__

    name = fields.Char(_('Name'), required=True)
    employee_id = fields.Many2one('hr.employee', string=_('Employee'))
    institution_id = fields.Many2one('hr.academic.institution', string=_(
        'Academic Institution'), ondelete='restrict')
    level = fields.Selection([('basic', _('Primary Education')),
                              ('secondary', _('Secondary Education')),
                              ('middle_school', _('Middle School')),
                              ('technical_superior', _('Technical Superior')),
                              ('university', _('University')),
                              ('postgraduate', _('Postgraduate')),
                              ('doctorate', _('Doctorate'))], string=_('Level'))
    knowledge_area = fields.Char(_('Knowledge Area'))
    date_start = fields.Date(_('Date Start'))
    date_stop = fields.Date(_('Date Stop'))
    state = fields.Selection([('culminated', _('Culminated')),
                              ('studying', _('Studying')),
                              ('graduated', _('Graduated')),
                              ('deferred', _('Deferred'))], string=_('State'))


class HrTrainings(models.Model):
    """
    Manage courses and trainings performed by employees
    """
    _name = 'hr.trainings'
    _description = __doc__

    name = fields.Char(_('Name'), required=True)
    employee_id = fields.Many2one('hr.employee', string=_('Employee'))
    institution_id = fields.Many2one('hr.academic.institution', string=_(
        'Academic Institution'), ondelete='restrict')
    modality = fields.Selection([('virtual', _('Virtual')),
                                 ('distance', _('Distance')),
                                 ('half-life', _('Half-life')),
                                 ('other', _('Other'))], string=_('Modality'))
    other = fields.Char(_('Other'))
    date_start = fields.Date(_('Date Start'))
    date_stop = fields.Date(_('Date Stop'))
    hours = fields.Float(_('Hours'))


class HrAcademicInstituition(models.Model):
    """
    Manage information from educational institutions
    """
    _name = 'hr.academic.institution'
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
