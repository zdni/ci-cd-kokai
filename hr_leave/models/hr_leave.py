from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime
import logging


_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    have_leave_quota = fields.Boolean('Have Leave Quota')
    leave_period_ids = fields.One2many('hr.leave.period', 'employee_id', string='Leave Period')
    leave_ids = fields.One2many('hr.leave', 'employee_id', string='Leave')
    leave_count = fields.Integer('Leave Count', compute='_compute_leave_count')
    @api.depends('leave_ids')
    def _compute_leave_count(self):
        for record in self:
            record.leave_count = len(record.leave_ids)

    def action_show_leave(self):
        self.ensure_one()
        action = self.env.ref('hr_leave.hr_leave_action').read()[0]
        action['domain'] = [('id', 'in', self.leave_ids.ids)]
        return action


class HrLeavePeriod(models.Model):
    _name = 'hr.leave.period'
    _description = 'Hr Leave Period'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    start_period = fields.Date('Start Period', tracking=True)
    end_period = fields.Date('End Period', tracking=True)
    limit = fields.Integer('Limit', default=12, tracking=True)
    reduce = fields.Integer('Leave Reduce Curr. Period', compute='_compute_reduce', tracking=True)

    @api.depends('employee_id.leave_ids.state')
    def _compute_reduce(self):
        for record in self:
            leave_used = sum([leave.total_date for leave in record.employee_id.leave_ids])
            record.reduce = record.limit - leave_used


class HrLeaveType(models.Model):
    _name = 'hr.leave.type'
    _description = 'Hr Leave Type'
    
    name = fields.Char('Name')
    is_reduce = fields.Boolean('Is Reduce')
    limit = fields.Integer('Limit')
    reduce_type = fields.Selection([
        ('dynamically', 'Dynamically'),
        ('fixed', 'Fixed'),
    ], string='Reduce Type', required=True, default='dynamically')
    total_used = fields.Float('Total Used')
    salary_rule = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], string='Salary Rule', default='paid', required=True)


class HRLeave(models.Model):
    _name = 'hr.leave'
    _description = 'Hr Leave'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    name = fields.Char('Name')
    type_id = fields.Many2one('hr.leave.type', string='Type', tracking=True)
    request_date = fields.Date('Request Date', tracking=True)
    start_date = fields.Datetime('Start Date', default=fields.Datetime.now(), tracking=True)
    end_date = fields.Datetime('End Date', tracking=True)
    total_date = fields.Float('Total Date', compute='_compute_total_date', store=True, tracking=True)
    reason = fields.Html('Reason', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, default='draft', tracking=True)
    attachment_type = fields.Selection([
        ('doctor_note', 'Doctor\' Note'),
        ('receipt', 'Receipt'),
        ('other', 'Other'),
    ], string='Attachment Type', required=True, default='doctor_note', tracking=True)
    attachment_name = fields.Char('Attachment Name', tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string='Attachment', tracking=True)
    note = fields.Html('Note', tracking=True)
    approval_id = fields.Many2one('approval.request', string='Approval', tracking=True)
    leave_used_ids = fields.One2many('hr.leave.used', 'leave_id', string='Leave Used')

    @api.depends('start_date', 'end_date')
    def _compute_total_date(self):
        for record in self:
            if record.end_date and record.start_date:
                record.total_date = (record.end_date - record.start_date).days + ((record.end_date - record.start_date).seconds/(3600))

    def _compute_leave_used(self):
        self.ensure_one()
        if not self.employee_id.have_leave_quota:
            raise ValidationError(f"You haven't Leave Quota")

        period = self.env['hr.leave.period'].search([
            ('employee_id', '=', self.employee_id.id),
            ('start_period', '<=', self.start_date),
        ], order='start_period DESC, id DESC')
        if not period or len(period) == 0:
            raise ValidationError(f"Can't Request Leave because You haven't Leave Quota. Please Contact HRD Team")
        
        if self.end_date > period[0].end_period:
            self.env['hr.leave.used'].create({
                'leave_id': self.id,
                'period_id': period[0].id,
                'total_used': ((period[0].end_period - self.start_date).seconds/(3600*24))
            })
            self.env['hr.leave.used'].create({
                'leave_id': self.id,
                'period_id': period[1].id,
                'total_used': ((self.end_date - period[1].start_period).seconds/(3600*24))
            })
        else:
            self.env['hr.leave.used'].create({
                'leave_id': self.id,
                'period_id': period[0].id,
                'total_used': self.total_date
            })
        

    def action_show_approval(self):
        self.ensure_one()
        if self.state in ['draft', 'cancel']:
            return
        action = self.env.ref('approvals.approval_request_action_all').read()[0]
        action['domain'] = [('id', '=', self.approval_id.id)]
        return action

    @api.onchange('attachment_type')
    def _onchange_attachment_type(self):
        for record in self:
            if record.attachment_type == 'other':
                record.attachment_name = ''
            else:
                record.attachment_name = record.attachment_type

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('hr.leave')
        return super(HRLeave, self).create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_request(self):
        self.ensure_one()
        category_pr = self.env.ref('hr_leave.approval_category_data_hr_leave')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'hr_leave_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for Leave {self.name} for {self.user_id.name} from {self.start_date} to {self.end_date}"
        }
        request = self.env['approval.request'].create(vals)
        request.action_confirm()
        self.write({ 'state': 'request', 'request_date': fields.Date.today(), 'approval_id': request.id })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Leave',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Leave {self.name} yang diajukan diterima. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.leave',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_refused(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Leave',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Leave {self.name} yang diajukan ditolak. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.leave',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'refused' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })


class HrLeaveUsed(models.Model):
    _name = 'hr.leave.used'
    _description = 'Hr Leave Used'

    leave_id = fields.Many2one('hr.leave', string='Leave')
    period_id = fields.Many2one('hr.leave.period', string='Period')
    total_used = fields.Float('Total Used')