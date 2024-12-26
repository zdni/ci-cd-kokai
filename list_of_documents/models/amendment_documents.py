from odoo import _, api, fields, models


class AmendmentDocument(models.Model):
    _name = 'amendment.document'
    _description = 'Amendment Document'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New')
    document_id = fields.Many2one('list.of.documents', string='Document', required=True)
    requested_date = fields.Date('Requested Date', required=True, default=fields.Date.today())
    approved_date = fields.Date('Approved Date', tracking=True)
    requested_by_id = fields.Many2one('res.users', string='Requested By', required=True, default=lambda self: self.env.user.id)
    approved_by_id = fields.Many2one('res.users', string='Approved By', tracking=True)
    amendment_article = fields.Char('Amendment Article', default='N/A', tracking=True)
    amendment_page = fields.Char('Amendment Page', default='N/A', tracking=True)
    amendment_section = fields.Char('Amendment Section', default='N/A', tracking=True)
    line_ids = fields.One2many('amendment.line', 'amendment_id', string='Content')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, default='draft', tracking=True)
    current_edition = fields.Integer('Current Edition', related='document_id.edition')
    new_edition = fields.Integer('New Edition', compute='_compute_new_edition')
    @api.depends('current_edition')
    def _compute_new_edition(self):
        for record in self:
            record.new_edition = record.current_edition + 1

    approval_ids = fields.One2many('approval.request', 'amendment_document_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_approval(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        action['domain'] = [('id', 'in', self.approval_ids.ids)]
        return action

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('amendment.document')
        return super(AmendmentDocument, self).create(vals) 

    def action_draft(self):
        self.ensure_one()
        self.write({ 'state': 'draft' })

    def action_requested(self):
        self.ensure_one()
        category_pr = self.env.ref('list_of_documents.approval_category_data_amendment_document')
        approval = self.env['approval.request'].create({
            'name': 'Request Approval for Amendment ' + self.name,
            'amendment_document_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for Amendment {self.name} from {self.requested_by_id.name} \n Amendment Document {self.document_id.name} is request Approval. Please review this amendment"
        })
        if approval:
            approval.action_confirm()
        self.write({ 'state': 'requested' })

    def action_approved(self):
        self.ensure_one()
        # notification to user
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Amendment Document',
            'user_id': self.requested_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by_id.name} \n Amandemen Dokumen {self.document_id.name} yang diajukan diterima. Silahkan lanjutkan proses berikutnya. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'amendment.document',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        # notification to user
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Amendment Document',
            'user_id': self.requested_by_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by_id.name} \n Amandemen {self.document_id.name} yang diajukan ditolak. Mohon diperbaiki dan ditinjau kembali sesuai dengan catatan yang ditinggalkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'amendment.document',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'need_improvement' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })

class AmendmentLine(models.Model):
    _name = 'amendment.line'
    _description = 'Amendment Line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    amendment_id = fields.Many2one('amendment.document', string='Amendment')
    before_amendment = fields.Text('Before Amendment', required=True, tracking=True)
    after_amendment = fields.Text('After Amendment', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need Improvement'),
        ('cancel', 'Cancel'),
    ], string='State', required=True, default='draft', tracking=True, related='amendment_id.state')