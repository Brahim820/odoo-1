#!/usr/bin/env python
# -*- coding: utf-8 -*-

from openerp import _, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academic_ids = fields.One2many(
        'hr.academic.training', 'employee_id', string=_('Academic Training'))
    training_ids = fields.One2many('hr.trainings', 'employee_id', string=_('Courses and Trainings'))
    experience_ids = fields.One2many('hr.work.experience', 'employee_id',
                                     string=_('Work Experience'))
