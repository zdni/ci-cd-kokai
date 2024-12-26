from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HROvertime(models.Model):
    _name = 'hr.overtime'
    _description = 'HR Overtime'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)

    name = fields.Char('Name', default='Overtime Request')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    reason = fields.Text('Reason')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', tracking=True)
    abs = fields.Char('Abs')
    hour_spent = fields.Float('Hour Spent', compute='_compute_hour_spent', store=True)
    @api.depends('start_date', 'end_date')
    def _compute_hour_spent(self):
        for record in self:
            record.hour_spent = 0

    approval_ids = fields.One2many('approval.request', 'hr_overtime_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', store=True)
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_approval(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = self.env.ref('approvals.approval_request_action_all').read()[0]
        action['domain'] = [('id', 'in', self.approval_ids.ids)]
        return action

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_requested(self):
        self.ensure_one()
        category_pr = self.env.ref('hr_overtime.approval_category_data_hr_overtime')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'hr_overtime_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for Overtime {self.name} for {self.user_id.name} from {self.start_date} to {self.end_date}"
        }
        request = self.env['approval.request'].create(vals)
        request.action_confirm()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Overtime',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Overtime {self.name} yang diajukan diterima. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.overtime',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_refused(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Overtime',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Overtime {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.overtime',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'refused' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('hr.overtime')
        return super(HROvertime, self).create(vals)


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    hr_overtime_ids = fields.One2many('hr.overtime', 'employee_id', string='Overtime')
    overtime_count = fields.Integer('Overtime Count', compute='_compute_overtime_count', store=True)
    limit_overtime = fields.Integer('Limit Overtime', default=12)
    @api.depends('hr_overtime_ids')
    def _compute_overtime_count(self):
        for record in self:
            record.overtime_count = len(record.hr_overtime_ids)

    def action_show_overtime(self):
        self.ensure_one()
        if self.overtime_count == 0:
            return
        action = self.env.ref('hr_overtime.hr_overtime_action').read()[0]
        action['domain'] = [('id', 'in', self.hr_overtime_ids.ids)]
        return action
