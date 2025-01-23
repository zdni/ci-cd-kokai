from odoo import _, api, fields, models
from odoo.exceptions import UserError

class CparType(models.Model):
    _name = 'cpar.type'
    _description = 'CAR Type'

    name = fields.Char('Name')
    alias = fields.Char('Alias')


class CparStandard(models.Model):
    _name = 'cpar.standard'
    _description = 'CPAR Standard'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary')
    standard_id = fields.Many2one('standard.manufacturing', string='QMS Specification', tracking=True)
    section = fields.Char('Section', tracking=True, compute='_compute_section', store=True)
    name = fields.Char('Clause', tracking=True)
    @api.depends('name')
    def _compute_section(self):
        for record in self:
            if record.name:
                record.section = record.name[:1]


class RootCauseCpar(models.Model):
    _name = 'root.cause.cpar'
    _description = 'Root Cause CPAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary', tracking=True)
    name = fields.Text('Root Cause', tracking=True)


class CorrectionCpar(models.Model):
    _name = 'correction.cpar'
    _description = 'Correction CPAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary', tracking=True)
    root_id = fields.Many2one('root.cause.cpar', string='Root Cause', tracking=True)
    name = fields.Text('Correction Action', tracking=True)
    pic_id = fields.Many2one('res.users', string='PIC', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open', tracking=True)


class CorrectiveCpar(models.Model):
    _name = 'corrective.cpar'
    _description = 'Corrective CPAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary', tracking=True)
    root_id = fields.Many2one('root.cause.cpar', string='Root Cause', tracking=True)
    name = fields.Text('Corrective Action', tracking=True)
    pic_id = fields.Many2one('res.users', string='PIC', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
    ], string='State', required=True, default='open', tracking=True)


class HistoryStateCpar(models.Model):
    _name = 'history.state.cpar'
    _description = 'History State CPAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary', tracking=True)
    name = fields.Char('State', tracking=True)
    old_state = fields.Char('Old State', tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)


class CommentCpar(models.Model):
    _name = 'comment.cpar'
    _description = 'Comment CPAR'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='Summary', tracking=True)
    name = fields.Text('Comment')
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True)


class SummaryCpar(models.Model):
    _name = 'summary.cpar'
    _description = 'Summary Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    name = fields.Char('Name', tracking=True)
    date = fields.Date('Date', tracking=True)
    car_no = fields.Char('CAR No.', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department')
    issued_to_ids = fields.Many2many('res.users', string='Issued To', domain="[('department_id', '=', department_id)]")
    type_id = fields.Many2one('cpar.type', string='Source of CAR')
    document_ids = fields.Many2many('list.of.documents', string='Controlling Documents')
    finding_type = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('concern', 'Concern'),
        ('ofi', 'OFI'),
        ('critical', 'Critical'),
    ], string='Finding Type', default='major', required=True, tracking=True)
    product_impact = fields.Selection([
        ('direct', 'Direct Impact'),
        ('indirect', 'Indirect Impact'),
        ('no', 'No Impact'),
    ], string='Product Impact', default='direct', required=True, tracking=True)
    standard_ids = fields.One2many('cpar.standard', 'summary_id', string='Standard Specification')
    description = fields.Text('Requirement Description', tracking=True)
    objective_evidence = fields.Html('Objective Evidence', tracking=True)
    description_nc = fields.Html('Description of Non-Conformance', tracking=True)
    root_ids = fields.One2many('root.cause.cpar', 'summary_id', string='Root Cause')
    correction_ids = fields.One2many('correction.cpar', 'summary_id', string='Correction Action')
    corrective_ids = fields.One2many('corrective.cpar', 'summary_id', string='Corrective Action')
    comment_ids = fields.One2many('comment.cpar', 'summary_id', string='Comments (if any) where the CAR was completed')
    action_verify = fields.Text('Action Performed to verify the effectiveness of CAR', tracking=True)
    history_ids = fields.One2many('history.state.cpar', 'summary_id', string='History State')
    state = fields.Selection([
        ('open', 'Open'),
        ('submit', 'Submit'),
        ('need_improvement', 'Need Improvement'),
        ('closed', 'Closed'),
    ], string='State', default='open', required=True, tracking=True)
    remarks = fields.Text('Remarks', tracking=True)

    def action_open(self):
        self.ensure_one()
        self.write({ 'state': 'open' })

    def action_submit(self):
        self.ensure_one()
        self.write({ 'state': 'submit' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })

    def action_closed(self):
        self.ensure_one()
        self.write({ 'state': 'closed' })

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            prefix = 'CAR'
            type = self.env['cpar.type'].search([ ('id', '=', val['type_id']) ], limit=1)
            if type:
                prefix = type.alias
            val['name'] = f"{prefix}/{self.env['ir.sequence'].next_by_code('summary.cpar')}"
        return super(SummaryCpar, self).create(vals)

    def write(self, vals):
        if vals.get('state', False):
            try:
                self.env['history.state.cpar'].create({
                    'name': vals['state'],
                    'summary_id': self.id,
                    'old_state': self.state,
                    'date': fields.Date.today(),
                })
            except UserError as e:
                raise UserError(str(e))
        return super(SummaryCpar, self).write(vals)


class ReportSummaryCpar(models.Model):
    _name = 'report.summary.cpar'
    _description = 'Report Summary Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name', tracking=True)
    description = fields.Text('description', tracking=True)
    date = fields.Date('Date', tracking=True)
    summary_ids = fields.Many2many('summary.cpar', string='List Summary', tracking=True)
    approval_id = fields.Many2one('approval.request', string='Approval', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user.id, tracking=True)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('summary.cpar')
        return super(ReportSummaryCpar, self).create(vals)

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_request(self):
        self.ensure_one()
        category_pr = self.env.ref('corrective_preventive_action.approval_category_data_report_summary_cpar')
        approval = self.env['approval.request'].create({
            'name': 'Request Approval for Summary CPAR ' + self.name,
            'report_summary_cpar_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for Summary CPAR {self.name} from {self.requested_by_id.name}. Please review this Report"
        })
        if approval:
            approval.action_confirm()
        self.write({ 'state': 'request' })

    def action_approved(self):
        self.ensure_one()
        # notification to user
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Summary CPAR',
            'user_id': self.requested_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by_id.name} \n Summary CPAR {self.name} yang diajukan diterima. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'report.summary.cpar',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_refused(self):
        self.ensure_one()
        # notification to user
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Summary CPAR',
            'user_id': self.requested_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by_id.name} \n Summary CPAR {self.name} yang diajukan ditolak. Mohon diperbaiki dan ditinjau kembali sesuai dengan catatan yang ditinggalkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'report.summary.cpar',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'refused' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })