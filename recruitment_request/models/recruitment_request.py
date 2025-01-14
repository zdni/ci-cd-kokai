from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class RecruitmentRequestStage(models.Model):
    _name = 'recruitment.request.stage'
    _description = 'Recruitment Request Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Maintenance Pipe')
    done = fields.Boolean('Request Done')


class RecruitmentRequest(models.Model):
    _name = 'recruitment.request'
    _description = 'Recruitment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['recruitment.request.stage'].search([], limit=1)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    
    stage_id = fields.Many2one('recruitment.request.stage', string='Stage', ondelete='restrict', tracking=True, group_expand='_read_group_stage_ids', default=_default_stage, copy=False)
    
    name = fields.Char('Name', default='New Request')
    request_by_id = fields.Many2one('res.users', string='Request By', default=lambda self: self.env.user.id)
    department_id = fields.Many2one('hr.department', string='Department', default=lambda self: self.env.user.department_id.id, tracking=True)
    job_id = fields.Many2one('hr.job', string='Job', domain="[('department_id', '=', department_id)]", tracking=True)
    target = fields.Integer('Target', default=1, tracking=True)
    description = fields.Html('Description')
    request_date = fields.Datetime('Request Date', default=fields.Datetime.now(), tracking=True)
    due_date = fields.Date('Due Date', tracking=True)
    specification = fields.Html('Employee Specification', related='job_id.description')

    reason_for_recruitment = fields.Selection([
        ('new', 'New'),
        ('replacement', 'Replacement'),
    ], string='Reason For Recruitment', default='new', tracking=True)
    reason = fields.Char('Reason')
    old_user_id = fields.Many2one('res.users', string='Old User', domain="[('department_id', '=', department_id)]")

    progressing_date = fields.Datetime('Progressing Date', tracking=True)
    closing_date = fields.Date('Closing Date', tracking=True)
    handle_by_id = fields.Many2one('res.users', string='Handle By', tracking=True)
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
    ], string='Priority', default='0', required=True)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Ready for next Stage'),
    ], string='Kanban State', required=True, default='normal')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Approval Request'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')

    applications_ids = fields.One2many('hr.applicant', 'request_id', string='Applications')
    applications_count = fields.Integer('Applications Count', compute='_compute_applications_count', store=True)
    @api.depends('applications_ids')
    def _compute_applications_count(self):
        for record in self:
            record.applications_count = len(record.applications_ids)

    def action_show_applications(self):
        self.ensure_one()
        if self.applications_count == 0:
            return
        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job').sudo().read()[0]
        action['domain'] = [('id', 'in', self.applications_ids.ids)]
        return action

    approval_ids = fields.One2many('approval.request', 'recruitment_request_id', string='Approval')
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

    allowance_ids = fields.One2many('allowance.submission', 'request_id', string='Allowance')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            sequence = 'recruitment.request'
            code = f"{sequence}.{self.env.user.department_id.alias}"
            check_sequence = self.env['ir.sequence'].search([('code', '=', code)], limit=1)
            if check_sequence:
                sequence = code
            
            val['name'] = self.env['ir.sequence'].next_by_code(sequence)
        return super(RecruitmentRequest, self).create(vals)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('component_inspection.approval_category_data_component_inspection')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'recruitment_request_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.request_by_id.name} \n Rekrutmen karyawan untuk {self.job_id.name}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'requested'
        })
        request = self.approval_ids[self.approval_count-1]
        request.action_confirm()

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_request(self):
        self.ensure_one()
        assignment = self.env['assignment.task'].sudo().create({
            'department_ids': [self.env.ref('department_detail.hr_management_data_hr_ga').id, self.env.ref('department_detail.hr_management_data_finance').id, self.env.ref('department_detail.hr_management_data_management').id],
            'user_id': self.env.user.id,
            'employee_type_ids': [self.env.ref('department_detail.hr_contract_type_head_of_department').id, self.env.ref('department_detail.hr_contract_type_senior_staff').id],
            'assigned_to': 'department',
            'subject': f"Permintaan Rekrutmen Karyawan",
            'description': f"Pemberitahuan untuk departemen terkait mengenai permintaan rekrutmen karyawan untuk posisi {self.job_id.name} sebanyak {self.target} orang. Mohon untuk segera diproses.",
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'model': 'recruitment.request',
            'res_id': self.id,
        })
        if not assignment:
            raise ValidationError("Can't Assignment Task! Please contact Administrator!")
        assignment.action_assign()
        self.write({ 'state': 'request', 'request_date': fields.Datetime.now() })

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Persetujuan Rekrutmen Karyawan',
            'user_id': self.request_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.request_by_id.name} \n Permintaan rekrutmen karyawan untuk posisi {self.job_id.name} telah disetujui. Proses akan  dilanjutkan ketahap berikutnya",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'recruitment.request',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Approval Rekrutmen Karyawan',
            'user_id': self.request_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.request_by_id.name} \n Permintaan rekrutmen karyawan untuk posisi {self.job_id.name} membutuhkan perbaikan. Silahkan cek kembali permintaan yang anda ajukan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'recruitment.request',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'need_improvement' })

    def action_refused(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Penolakan Rekrutmen Karyawan',
            'user_id': self.request_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.request_by_id.name} \n Permintaan rekrutmen karyawan untuk posisi {self.job_id.name} membutuhkan ditolak. Silahkan cek alasan penolakan untuk permintaan yang anda ajukan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'recruitment.request',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'refused' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })


class AllowanceSubmission(models.Model):
    _name = 'allowance.submission'
    _description = 'Allowance Submission'
    _inherit = ['mail.activity.mixin', 'mail.thread']

    request_id = fields.Many2one('recruitment.request', string='Request')
    allowance_type_id = fields.Many2one('hr.allowance.type', string='Allowance Type')
    name = fields.Char('Name', related='allowance_type_id.name')
    offering = fields.Float('Offering')
    finance_offering = fields.Float('Finance Offering', tracking=True)
    state = fields.Selection([
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string='Status', tracking=True)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    request_id = fields.Many2one('recruitment.request', string='Request')