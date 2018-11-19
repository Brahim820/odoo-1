# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import datetime, timedelta

from dateutil import relativedelta
from lxml import etree
from openerp import _, api, fields, models
from openerp.exceptions import UserError, ValidationError
from openerp.tools import drop_view_if_exists, float_compare, float_is_zero

month_days = [
    ('01', '01'),
    ('02', '02'),
    ('03', '03'),
    ('04', '04'),
    ('05', '05'),
    ('06', '06'),
    ('07', '07'),
    ('08', '08'),
    ('09', '09'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
]


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    analytic = fields.Boolean('Analytic', help=_(
        'Check this box if you want to keep an analytical record for this salary rule'), default=False)
    biweekly_deduction = fields.Boolean(_('Biweekly Deduction'), help=_(
        'Check this option if this item should be deducted in the monthly payment roll'))


class HrPayslipType(models.Model):
    """
    Model to manage Type of Payslip
    """
    _name = 'hr.payslip.type'

    name = fields.Char(_('Name'))
    description = fields.Text(_('Description'))
    day_from = fields.Selection(month_days, string=_('Day From'))
    day_to = fields.Selection(month_days, string=_('Day To'))
    exclude_entry = fields.Selection(month_days, string=_(
        'Entry Exclude'), help=_('Eclude to payslip if contract date start'))


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_partner_id(self, map_id, payslip_line, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        partner_id = map_id.partner_id.id or payslip_line.salary_rule_id.register_id.partner_id.id or payslip_line.slip_id.employee_id.address_home_id.id
        if map_id:
            if credit_account:
                if map_id.account_credit.internal_type in ('receivable', 'payable'):
                    return partner_id
            else:
                if map_id.account_debit.internal_type in ('receivable', 'payable'):
                    return partner_id
        if credit_account:
            if payslip_line.salary_rule_id.register_id.partner_id or payslip_line.salary_rule_id.account_credit.internal_type in ('receivable', 'payable'):
                return partner_id
        else:
            if payslip_line.salary_rule_id.register_id.partner_id or payslip_line.salary_rule_id.account_debit.internal_type in ('receivable', 'payable'):
                return partner_id
        return False


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _order = 'date_start'

    @api.multi
    def undo_payslip_run(self):
        for row in self:
            row.slip_ids.undo_sheet()
            row.write({'state': 'draft'})

    @api.multi
    def post_payslip_run(self):
        for row in self:
            row.slip_ids.post_sheet()

    @api.multi
    def print_hr_payslip_run(self):
        wizard_form = self.env.ref(
            'l10n_ec_hr_payroll.view_wizard_hr_payroll_print', False)
        return {
            'name': _('Print {}'.format(self.name)),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.hr.payroll.print',
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new'
        }

    @api.multi
    def compute_sheet(self):
        for row in self:
            row.slip_ids.compute_sheet()

    @api.multi
    def confirm_payslip_run(self):
        for row in self:
            row.slip_ids.filtered(lambda x: x.exclude is False).process_sheet()
            row.write({'state': 'confirm'})

    @api.multi
    def action_spi(self):
        wiz_obj = self.env['wizard.hr.payslip.spi']
        wiz_id = wiz_obj.create({
            'slip_id': self.id,
            'partner_id': self.company_id.partner_id.id,
            'payment_date': self.date_end
        })
        return {
            'name': _("Generate Cash Management"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'wizard.hr.payslip.spi',
            'res_id': wiz_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context
        }

    def _get_default_company(self):
        return self.env.user.company_id

    def _get_default_journal(self):
        res = self.env.user.company_id.default_payroll_journal_id
        if res:
            return res
        return False

    @api.multi
    @api.depends('slip_ids')
    def _get_slip_pay_amount(self):
        transfer = 0
        check = 0
        exclude = 0
        for row in self:
            for slip in row.slip_ids:
                if not slip.exclude:
                    if slip.employee_id.bank_account_id:
                        transfer += slip.amount
                    else:
                        check += slip.amount
                else:
                    exclude += slip.amount
            row.transfer_amount = transfer
            row.check_amount = check
            row.exclude_amount = exclude
            row.amount = transfer + check

    department_id = fields.Many2one('hr.department', string=_('Department'), help=_(
        'Fill this box to generate a department payment role'))
    payment_ids = fields.One2many(
        'account.payment', 'payroll_slip_run_id', string=_('Payments'))
    payroll_type = fields.Many2one(
        'hr.payslip.type', string='Payroll Type', required=True)
    journal_id = fields.Many2one(default=_get_default_journal, )
    company_id = fields.Many2one('res.company', _('Company'), required=True,
                                 readonly=True, default=_get_default_company)
    state = fields.Selection(
        selection_add=[('confirm', _('Confirm')), ('paid', _('Paid'))])
    transfer_amount = fields.Float('Amount to pay by transfer',
                                   compute=_get_slip_pay_amount)
    check_amount = fields.Float(
        'Amount to pay by check', compute=_get_slip_pay_amount)
    exclude_amount = fields.Float(
        'Exclude amount', compute=_get_slip_pay_amount)
    amount = fields.Float('Amount to pay', compute=_get_slip_pay_amount)
    date = fields.Date('Date Account', required=True, default=fields.Date.today(),
                       help="Keep empty to use the period of the validation(Payslip) date.")

    transfer_count = fields.Integer(
        compute='_compute_payment_ids', string='# Transfers')
    transfer_ids = fields.Many2many(
        'account.payment', compute='_compute_payment_ids', string='Payment associated to this Payslip')
    check_count = fields.Integer(
        compute='_compute_payment_ids', string='# Checks')
    check_ids = fields.Many2many(
        'account.payment', compute='_compute_payment_ids', string='Payment associated to this Payslip')

    @api.multi
    @api.depends('slip_ids.payment_ids')
    def _compute_payment_ids(self):
        for row in self:
            slip_ids = row.mapped('slip_ids')
            row.transfer_ids = slip_ids.filtered(
                lambda x: x.payment_type == 'transfer').mapped('payment_ids').ids if slip_ids.mapped('payment_ids') else []
            row.transfer_count = len(row.transfer_ids)
            row.check_ids = slip_ids.filtered(
                lambda x: x.payment_type == 'check').mapped('payment_ids').ids if slip_ids.mapped('payment_ids') else []
            row.check_count = len(row.check_ids)

    @api.multi
    def action_view_transfers(self):
        context = {'tree_view_ref': 'account.view_account_supplier_payment_tree'}
        return {
            'name': _('Transfers for {}'.format(self.name)),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('transfer_ids').ids)],
            'context': context,
        }

    @api.multi
    def action_view_checks(self):
        context = {'tree_view_ref': 'account.view_account_supplier_payment_tree'}
        return {
            'name': _('Checks for {}'.format(self.name)),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('check_ids').ids)],
            'context': context,
        }

    @api.one
    @api.onchange('date_start', 'payroll_type')
    def _onchange_date_start(self):
        date_start = datetime.strptime(self.date_start, '%Y-%m-%d')
        self.name = '{prefix} {type} {month}-{year}'.format(prefix=_(
            'BP'), type=self.payroll_type.name, month=date_start.strftime("%m"), year=date_start.year).upper()
        date_end = date_start + \
            relativedelta.relativedelta(months=+1, day=1, days=-1)
        if int(self.payroll_type.day_to) <= 15:
            date_end = date_start + relativedelta.relativedelta(day=15)
        self.date_end = str(date_end)[:10]


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def print_hr_payslip(self):
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'l10n_ec_hr_payroll.hr_payslip_report')

    def get_contract(self, cr, uid, employee, date_from, date_to, context=None):
        contract_obj = self.pool.get('hr.contract')
        clause_final = [('employee_id', '=', employee.id)]
        contract_ids = contract_obj.search(
            cr, uid, clause_final, context=context)
        return contract_ids

    @api.multi
    def _compute_pay_amount(self):
        line_obj = self.env['hr.payslip.line']
        # TODO LIQ se deja por compatibilidad, una vez pagados los sueldos con LIQ, dejar solo NET.
        for row in self:
            if row.state in ('draft', 'verify', 'done'):
                liquido = line_obj.search(
                    [('code', 'in', ('NET', 'LIQ')), ('slip_id', '=', row.id)])
                row.amount = liquido.amount

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = models.Model.fields_view_get(
            self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        update = view_type in ['form', 'tree']
        if update:
            doc = etree.XML(res['arch'])
            for t in doc.xpath("//" + view_type):
                t.attrib['create'] = 'false'
            res['arch'] = etree.tostring(doc)
        return res

    def _get_default_journal(self):
        res = self.env.user.company_id.default_payroll_journal_id
        if res:
            return res
        return False

    def _get_default_company(self):
        return self.env.user.company_id

    @api.multi
    def _get_payment_type(self):
        res = ''
        for row in self:
            if row.employee_id.bank_account_id:
                res = 'transfer'
            else:
                res = 'check'
            row.payment_type = res

    payroll_type = fields.Many2one(
        'hr.payslip.type', string='Payroll Type', required=True)
    payment_ids = fields.One2many(
        'account.payment', 'payroll_slip_id', string=_('Payment'))
    journal_id = fields.Many2one(default=_get_default_journal, )
    company_id = fields.Many2one('res.company', _('Company'), required=True,
                                 readonly=True, default=_get_default_company)
    payment_type = fields.Selection([('check', 'Check'),
                                     ('transfer', 'Transfer')], string='Payment Type', compute=_get_payment_type)
    amount = fields.Float('Amount to pay', compute=_compute_pay_amount)
    exclude = fields.Boolean('Exclude')

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def check_contract_attendance(contract, day):
            res = True
            if contract.date_start:
                start_day = datetime.strptime(contract.date_start, "%Y-%m-%d")
                if day >= start_day:
                    if contract.date_end:
                        end_day = datetime.strptime(
                            contract.date_end, "%Y-%m-%d")
                        if day <= end_day:
                            res = False
                    else:
                        res = False
            return res

        def was_on_leave(employee_id, datetime_day, context=None):
            res = {}
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', day),
                ('date_to', '>=', day)])
            if holiday_ids:
                res['data'] = self.pool.get('hr.holidays').browse(
                    cr, uid, holiday_ids, context=context)[0]
                res['type'] = 'ausent'
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(date_from, "%Y-%m-%d")

            nb_of_days = range(0, 30)
            for day in nb_of_days:
                leave_type = was_on_leave(contract.employee_id.id, day_from +
                                          timedelta(days=day), context=context)
                leave_contract = check_contract_attendance(
                    contract, day_from + timedelta(days=day))

                """ El número de días trabajados siempre es 30, indistintamente del número real de días
                    en el mes. ¿Debemos permitir que el número de días pueda ser variable? """
                # attendances['number_of_days'] = 30
                if leave_type:
                    # the employee had to work
                    if leave_type['data'] in leaves:
                        leaves[leave_type['data']]['number_of_days'] += 1.0
                    elif leave_type['type'] == 'ausent':
                        leaves[leave_type['data']] = {
                            'name': leave_type['data'].holiday_status_id.name,
                            'sequence': 5,
                            'code': leave_type['data'].holiday_status_id.code or '',
                            'number_of_days': 1.0,
                            'contract_id': contract.id,
                        }
                else:
                    if leave_contract:
                        pass
                    else:
                        attendances['number_of_days'] += 1.0
            leaves = [value for key, value in leaves.items()]
            res += [attendances] + leaves
        return res

    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(
                    localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict[
                'categories'].dict and localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):

            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                res = 0.0
                self.cr.execute("SELECT sum(amount) as sum\
                            FROM hr_payslip as hp, hr_payslip_input as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                                (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class Sri(BrowsableObject):

            def tax_rent(self, contract, date_from, projectable, non_projectable, iess_percent):
                rent_tax_obj = self.pool.get('hr.sri.rent.tax')
                annual_tax_obj = self.pool.get('hr.sri.annual.rent.tax')
                amount = 0.0
                month = str(date_from)[5:7]
                year = str(date_from)[0:4]
                annual_id = None
                if contract.rent_tax_ids:
                    for row in contract.rent_tax_ids:
                        if row.year == year:
                            annual_id = row.id
                            if row.line_ids:
                                for line in row.line_ids:
                                    if line.month == month:
                                        rent_tax_obj.unlink(
                                            self.cr, self.uid, line.id)
                else:
                    annual_id = annual_tax_obj.create(self.cr, self.uid, {
                        'name': 'Rent Tax %s' % year,
                        'year': year,
                        'contract_id': contract.id
                    })
                base = projectable + non_projectable
                iess = base * iess_percent
                base -= iess

                deductible = 0
                if contract.projection_ids:
                    for row in contract.projection_ids:
                        if row.year == year:
                            deductible = row.monthly_amount

                table_obj = self.pool.get('hr.sri.retention')
                line_obj = self.pool.get('hr.sri.retention.line')

                table_ids = table_obj.search(self.cr, self.uid, [('year', '=', year),
                                                                 ('active', '=', True)])
                if table_ids:
                    for row in table_obj.browse(self.cr, self.uid, table_ids):
                        max_deductible = row.max_deductible / 12.0
                        if max_deductible < deductible and max_deductible > 0:
                            deductible = max_deductible
                        base -= deductible

                        line_ids = line_obj.search(self.cr, self.uid, [('ret_id', '=', row.id),
                                                                       ('monthly_basic_fraction',
                                                                        '<=', base),
                                                                       ('monthly_excess_up', '>=', base)])
                        for line in line_obj.browse(self.cr, self.uid, line_ids):
                            amount += line.monthly_basic_fraction_tax
                            amount += (((base - line.monthly_basic_fraction)
                                        * line.percent) / 100.0)
                            rent_tax_obj.create(self.cr, self.uid, {'year': year,
                                                                    'month': month,
                                                                    'projectable': projectable,
                                                                    'non_projectable': non_projectable,
                                                                    'amount': round(amount, 2),
                                                                    'rent_id': annual_id})
                if amount > 0:
                    return amount
                return 0

        class Utils(BrowsableObject):

            def check_reserve_funds(self, contract, payslip):
                date_format = '%Y-%m-%d'
                cdate = datetime.strptime(contract.date_start, date_format)
                pdate = datetime.strptime(payslip.date_to, date_format)
                tdays = (pdate - cdate).days
                if tdays > 365:
                    return True
                return False

            def reserve_funds(self, contract, payslip, inggrav, work100, fr_percent, method):
                date_format = '%Y-%m-%d'
                total = 0.0
                cdate = datetime.strptime(contract.date_start, date_format)
                pdate = datetime.strptime(payslip.date_from, date_format)
                tdays = (pdate - cdate).days + work100
                sub_total = inggrav * (fr_percent / 100.0)
                if (tdays - 395) >= 0:
                    total = sub_total
                else:
                    total = (sub_total / 30.0) * (tdays - 365.0)
                amount = total

                if method == 'payslip':
                    type_obj = self.pool.get('hr.payslip.type')
                    type_id = type_obj.search(
                        self.cr, self.uid, [('name', '=', 'Mensual')])
                    payslip_obj = self.pool.get('hr.payslip')
                    line_obj = self.pool.get('hr.payslip.line')
                    payslip_date = datetime.strptime(
                        payslip.date_from, date_format) - relativedelta.relativedelta(months=1)
                    date_from = '{}-{:0>2}-{:0>2}'.format(payslip_date.year,
                                                          payslip_date.month, payslip_date.day)
                    date_to = '{}-{:0>2}-{:0>2}'.format(payslip_date.year, payslip_date.month,
                                                        monthrange(payslip_date.year, payslip_date.month)[1])
                    payslip_id = payslip_obj.search(self.cr, self.uid, [
                        ('contract_id', '=', contract.id),
                        ('date_from', '>=', date_from),
                        ('date_to', '<=', date_to),
                        ('payroll_type', 'in', type_id)
                    ])
                    line_id = line_obj.search(self.cr, self.uid, [('slip_id', 'in', payslip_id),
                                                                  ('code', '=', 'FRPROV')])
                    if line_id:
                        amount = sum(
                            [prov.amount for prov in line_obj.browse(self.cr, self.uid, line_id)])
                return amount

            def biweekly(self, employee, contract, date_from, date_to):
                amount = 0.0
                type_obj = self.pool.get('hr.payslip.type')
                payslip_obj = self.pool.get('hr.payslip')
                rule_obj = self.pool.get('hr.salary.rule')
                line_obj = self.pool.get('hr.payslip.line')
                type_id = type_obj.search(
                    self.cr, self.uid, [('name', '=', 'Quincenal')])
                rule_id = rule_obj.search(
                    self.cr, self.uid, [('biweekly_deduction', '=', True)])
                payslip_id = payslip_obj.search(self.cr, self.uid, [
                    ('contract_id', '=', contract.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', date_to),
                    ('payroll_type', 'in', type_id),
                ])
                if payslip_id and rule_id:
                    line_id = line_obj.search(self.cr, self.uid, [
                        ('salary_rule_id', 'in', rule_id),
                        ('slip_id', 'in', payslip_id)])
                    if line_id:
                        amount = sum(
                            [ded.amount for ded in line_obj.browse(self.cr, self.uid, line_id)])
                if amount > 0:
                    return amount
                return 0

            def invoices(self, employee, date_from, date_to):
                amount = 0.0
                payment_obj = self.pool.get('account.payment')
                journal_obj = self.pool.get('account.journal')
                journal_id = journal_obj.search(
                    self.cr, self.uid, [('name', '=', 'DESCUENTO EN ROL')])
                partner_id = employee.address_home_id.id
                payment_id = payment_obj.search(self.cr, self.uid, [
                    ('partner_id', '=', partner_id),
                    ('journal_id', '=', journal_id),
                    ('payment_date', '>=', date_from),
                    ('payment_date', '<=', date_to),
                    ('state', '=', 'posted')
                ])
                if payment_id:
                    amount = sum([pay.amount for pay in payment_obj.browse(
                        self.cr, self.uid, payment_id)])
                if amount > 0:
                    return amount
                return 0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours\
                            FROM hr_payslip as hp, hr_payslip_worked_days as pi \
                            WHERE hp.employee_id = %s AND hp.state = 'done'\
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s",
                                (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)\
                            FROM hr_payslip as hp, hr_payslip_line as pl \
                            WHERE hp.employee_id = %s AND hp.state = 'done' \
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s",
                                (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by
        # another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        inputs_vals = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(
            self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(self.pool, cr, uid,
                              payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(
            self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(
            self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(
            self.pool, cr, uid, payslip.employee_id.id, rules)

        sri_obj = Sri(self.pool, cr, uid, payslip.employee_id.id, payslip_obj)
        utils_obj = Utils(self.pool, cr, uid,
                          payslip.employee_id.id, payslip_obj)
        baselocaldict = {'categories': categories_obj, 'rules': rules_obj, 'payslip': payslip_obj,
                         'worked_days': worked_days_obj, 'inputs': input_obj, 'sri': sri_obj,
                         'utils': utils_obj}
        # get the ids of the structures on the contracts and their parent id as well
        structure_ids = self.pool.get('hr.contract').get_all_structures(
            cr, uid, contract_ids, context=context)
        # get the rules of the structure and thier children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(
            cr, uid, structure_ids, context=context)
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(
            rule_ids, key=lambda x:x[1])]

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee,
                             contract=contract)
            for rule in obj_rule.browse(cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if obj_rule.satisfy_condition(cr, uid, rule.id, localdict, context=context) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = obj_rule.compute_rule(
                        cr, uid, rule.id, localdict, context=context)
                    # sum inputs amount
                    if rule.code in inputs_vals:
                        amount = inputs_vals[rule.code]['amount']
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(
                        localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in self.pool.get(
                        'hr.salary.rule')._recursive_search_of_rules(cr, uid, [rule], context=context)]

        result = [value for code, value in result_dict.items()]
        return result

    @api.multi
    def compute_worked_days(self):
        for payslip in self:
            worked_days_ids = payslip.mapped('worked_days_line_ids')
            if worked_days_ids:
                # delete old worked days lines
                worked_days_ids.unlink()

            contract_ids = payslip.contract_id.ids or \
                self.get_contract(
                    payslip.employee_id, payslip.date_from, payslip.date_to)
            worked_days = [(0, 0, worked_days) for worked_days in self.get_worked_day_lines(
                contract_ids, payslip.date_from, payslip.date_to)]
            payslip.write({'worked_days_line_ids': worked_days})
        return True

    @api.one
    def process_sheet(self):
        return self.write({'paid': True, 'state': 'done'})

    @api.multi
    def post_sheet(self):
        move_pool = self.env['account.move']
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for slip in self:
            if slip.exclude:
                continue
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.payslip_run_id.date or slip.date or slip.date_to

            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue
                debit_account_id = False
                credit_account_id = False
                analytic_account_id = False
                tax_line_id = False
                if slip.contract_id.department_id:
                    department_id = slip.contract_id.department_id
                    while department_id:
                        map_id = department_id.mapped('salaryrule_map_ids').filtered(
                            lambda x: x.department_id.id == department_id.id and x.salary_rule_id.id == line.salary_rule_id.id)
                        if map_id:
                            break
                        else:
                            department_id = department_id.parent_id
                    if map_id:
                        debit_account_id = map_id.account_debit and map_id.account_debit.id
                        credit_account_id = map_id.account_credit and map_id.account_credit.id
                        analytic_account_id = map_id.analytic_account_id and map_id.analityc_account_id.id
                        tax_line_id = map_id.account_tax_id and map_id.account_tax_id.id
                else:
                    debit_account_id = line.salary_rule_id.account_debit.id
                    credit_account_id = line.salary_rule_id.account_credit.id
                    analytic_account_id = line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False
                    tax_line_id = line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False
                if line.salary_rule_id.analytic:
                    analytic_account_id = line.mapped('employee_id').mapped(
                        'job_id').mapped('analytic_account_id').id
                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(map_id, line, credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        'analytic_account_id': analytic_account_id,
                        'tax_line_id': tax_line_id
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - \
                        debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(map_id, line, credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        'analytic_account_id': analytic_account_id,
                        'tax_line_id': tax_line_id
                    })
                    line_ids.append(credit_line)

                    credit_sum += credit_line[2]['credit'] - \
                        credit_line[2]['debit']
            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                        slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                        slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            if not slip.move_id:
                move['line_ids'] = line_ids
                move_id = move_pool.create(move)
                move_id.post()
                slip.write({
                    'move_id': move_id.id,
                    'date': date
                })
        return True

    @api.multi
    def update_sheet(self):
        self.compute_worked_days()
        self.compute_sheet()
        return True

    @api.multi
    def undo_sheet(self):
        for row in self:
            if row.move_id.state == 'posted':
                raise ValidationError(
                    _('You can not re-draft a payment role that has already been posted!'))
            row.write({'paid': False, 'state': 'draft'})


class PayrollReportView(models.Model):
    _name = 'hr.payroll.report.view'
    _auto = False

    name = fields.Many2one('hr.employee', string='Employee')
    payroll_type = fields.Many2one(
        'hr.payslip.type', string='Payroll Type', required=True)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    state = fields.Selection([('draft', 'Draft'), ('verify', 'Waiting'), ('done', 'Done'), ('cancel', 'Rejected')],
                             string='Status')
    job_id = fields.Many2one('hr.job', string='Job Title')
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', string='Department')
    net = fields.Float(string='Net Salary')

    def _select(self):
        select_str = """
        min(ps.id) as id,emp.id as name,jb.id as job_id,
        dp.id as department_id,cmp.id as company_id, ps.payroll_type,
        ps.date_from, ps.date_to, sum(psl.total) as net, ps.state as state
        """
        return select_str

    def _from(self):
        from_str = """
            hr_payslip_line psl  join hr_payslip ps on (ps.employee_id=psl.employee_id and ps.id=psl.slip_id)
            join hr_employee emp on (ps.employee_id=emp.id) join hr_department dp on (emp.department_id=dp.id)
            join hr_job jb on (emp.job_id=jb.id) join res_company cmp on (cmp.id=ps.company_id) where psl.code='NET'
         """
        return from_str

    def _group_by(self):
        group_by_str = """
            group by emp.id,psl.total,ps.payroll_type,ps.date_from, ps.date_to, ps.state,jb.id,dp.id,cmp.id
        """
        return group_by_str

    def init(self, cr):
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
               %s
               FROM %s
               %s
               )""" % (self._table, self._select(), self._from(), self._group_by()))
