from odoo import _, api, fields, models
from datetime import datetime, timedelta
from odoo.tools.safe_eval import safe_eval


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    bank_id = fields.Many2one('res.bank', string='Bank', tracking=True)
    account_number = fields.Char('Account Number', tracking=True)
    owner_name = fields.Char('Owner Name', tracking=True)
    payslip_ids = fields.One2many('hr.payslip', 'employee_id', string='Payslip')

    def action_show_payslip(self):
        self.ensure_one()


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_state_id = fields.Many2one('hr.contract.state', string='Contract Status', tracking=True)
    allowance_ids = fields.One2many('hr.contract.allowance', 'contract_id', string='Allowance')


class HrContractAllowance(models.Model):
    _name = 'hr.contract.allowance'
    _description = 'Hr Contract Allowance'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    
    contract_id = fields.Many2one('hr.contract', string='Contract')
    allowance_id = fields.Many2one('hr.allowance.type', string='Allowance', tracking=True)
    type = fields.Selection([
        ('main', 'Main'),
        ('addition', 'Addition'),
        ('subtraction', 'Subtraction'),
        ('formula', 'Formula'),
    ], string='Type', default='main', related='allowance_id.type')
    is_get = fields.Boolean('Get?', default=True)
    value = fields.Float('Value', tracking=True)


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _description = 'Hr Payslip'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', tracking=True)

    start_period = fields.Date('Start Period', tracking=True)
    end_period = fields.Date('End Period', tracking=True)
    total_days = fields.Integer('Total Days', compute='_compute_total_days', store=True, tracking=True)
    total_holidays = fields.Integer('Total Holidays', tracking=True)
    total_working_days = fields.Integer('Total Working Days', compute='_compute_total_working_days', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking=True)
    line_ids = fields.One2many('hr.payslip.line', 'payslip_id', string='Line')
    total_payslip = fields.Float('Total Payslip', compute='_compute_total_payslip', store=True, tracking=True)
    leave_ids = fields.One2many('hr.payslip.leave', 'payslip_id', string='Leave')
    remaining_leave = fields.Float('Remaining Leave', tracking=True)

    @api.depends('start_period', 'end_period')
    def _compute_total_days(self):
        for record in self:
            num_business_days = 0
            current_date = record.start_period
            while current_date <= record.end_period:
                if current_date.weekday() < 5:
                    num_business_days += 1
                current_date += timedelta(days=1)
            record.total_days = num_business_days
    
    @api.depends('total_days', 'total_holidays')
    def _compute_total_working_days(self):
        for record in self:
            record.total_working_days = record.total_days - record.total_holidays

    @api.depends('line_ids')
    def _compute_total_payslip(self):
        for record in self:
            record.total_payslip = sum([line.value if line.allowance_id.type in ['main', 'addition'] else -1*line.value for line in record.line_ids])

    def _compute_payslip(self):
        self.ensure_one()
        # safe_eval()

    def _get_localdict(self):
        self.ensure_one()
        allowances = {}
        localdict = {
            'allowances': allowances,
            'contract': self.contract_id,
            'employee': self.employee_id,
            'total_working_days': self.total_working_days,
            'leave': self.leave_ids,
        }
        return localdict


class HrPayslipLine(models.Model):
    _name = 'hr.payslip.line'
    _description = 'Hr Payslip Line'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    allowance_id = fields.Many2one('hr.allowance.type', string='Allowance')
    value = fields.Float('Value')


class HrPayslipLeave(models.Model):
    _name = 'hr.payslip.leave'
    _description = 'Hr Payslip Leave'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    leave_id = fields.Many2one('hr.leave.type', string='leave')
    value = fields.Float('Value')