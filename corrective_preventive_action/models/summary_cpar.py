from odoo import _, api, fields, models


class SummaryCpar(models.Model):
    _name = 'summary.cpar'
    _description = 'Summary Corrective - Preventive Action'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    name = fields.Char('Name', tracking=True)
    finding_number = fields.Char('Finding Number', tracking=True)
    date = fields.Date('Date', tracking=True)
    ncr_number = fields.Char('NCR Number', tracking=True)
    pic_id = fields.Many2one('res.users', string='PIC', tracking=True)
    finding_type = fields.Selection([
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('observe', 'OFI/Observe'),
        ('critical', 'Critical'),
    ], string='Finding Type', default='major', required=True, tracking=True)
    product_impact = fields.Selection([
        ('direct', 'Direct'),
        ('indirect', 'Indirect'),
        ('no', 'No Impact'),
    ], string='Product Impact', default='direct', required=True, tracking=True)
    qms_specification_id = fields.Many2one('standard.manufacturing', string='QMS Specification', tracking=True)
    section = fields.Char('Section', tracking=True)
    clause = fields.Char('Clause', tracking=True)
    description = fields.Text('Requirement Description', tracking=True)
    objective_evidence = fields.Char('Objective Evidence', tracking=True)
    define_problem = fields.Text('Define Problem', tracking=True)
    root_cause = fields.Text('Root Cause', tracking=True)
    counter_ids = fields.One2many('counter.measure.cpar', 'summary_id', string='Counter Measure', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', default='open', required=True, tracking=True, compute='_compute_state', store=True)
    remarks = fields.Text('Remarks', tracking=True)

    @api.depends('counter_ids.state')
    def _compute_state(self):
        for record in self:
            record.state = 'closed' if all(counter.state == 'closed' for counter in record.counter_ids) else 'open'

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('summary.cpar')
        return super(SummaryCpar, self).create(vals)


class CounterMeasureCpar(models.Model):
    _name = 'counter.measure.cpar'
    _description = 'Counter Measure Cpar'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    summary_id = fields.Many2one('summary.cpar', string='CPAR', tracking=True)
    name = fields.Char('Counter', tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    completion_date = fields.Date('Completion Date', tracking=True)
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='State', default='open', required=True, tracking=True)



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