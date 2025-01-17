from odoo import _, api, fields, models


class SummaryCpar(models.Model):
    _name = 'summary.cpar'
    _description = 'Summary Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    name = fields.Char('Name')
    finding_number = fields.Char('Finding Number')
    date = fields.Date('Date')
    ncr_number = fields.Char('NCR Number')
    pic_id = fields.Many2one('res.users', string='PIC')
    finding_type = fields.Char('Finding Type')
    product_impact = fields.Char('Product Impact')
    qms_specification = fields.Char('QMS Specification')
    clause = fields.Char('clause')
    description = fields.Text('Requirement Description')
    objective_evidence = fields.Char('Objective Evidence')
    define_problem = fields.Text('Define Problem')
    root_cause = fields.Char('Root Cause')
    counter_measure = fields.Char('Counter Measure')
    completion_date = fields.Date('Completion Date')
    state = fields.Selection([
        ('draft', 'Draft'),
    ], string='State')
    remarks = fields.Text('Remarks')


class ReportSummaryCpar(models.Model):
    _name = 'report.summary.cpar'
    _description = 'Report Summary Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    description = fields.Text('description')
    date = fields.Date('Date')
    summary_ids = fields.Many2many('summary.cpar', string='List Summary')
    approval_id = fields.Many2one('approval.request', string='Approval')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')
    requested_by_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user.id)

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