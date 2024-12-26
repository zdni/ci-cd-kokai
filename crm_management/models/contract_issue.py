from odoo import _, api, fields, models

class ContractIssue(models.Model):
    _name = 'contract.issue'
    _description = 'Issue in FIR or FRK'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'issue_date'

    order_id = fields.Many2one('sale.order', string='Order')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    name = fields.Char('Name', default='New')
    issue_date = fields.Datetime('Issue Date', default=fields.Datetime.now())
    description = fields.Text('Description', default='-')
    prepared_id = fields.Many2one('res.users', string='Prepared') # everyone in assign inquiry review can't be prepared user and get notification when issue created
    issue_solve = fields.Text('Issue Solve', default='-')
    solve_date = fields.Datetime('Solve Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Request'),
        ('approved', 'Approved'),
        ('need_improvement', 'Need_improvement'),
        ('cancel', 'Cancel'),
    ], string='State', default='request', required=True)
    approver_ids = fields.Many2many('res.users', string='Approver')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('contract.issue')
        return super(ContractIssue, self).create(vals)

    def generate_approval_request(self):
        self.ensure_one()
        category_pr = self.env.ref('crm_management.approval_category_data_contract_issue')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'issue_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.user_id.name} \n Issue in {self.order_id.name} has been done solved, Please review and approved or refused"
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
        self.generate_approval_request()
        self.write({ 'state': 'request' })

    def action_approved(self):
        self.ensure_one()
        # notification to user
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approved Contract Issue',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Penyelesaian Issue {self.name} yang diajukan diterima. Silahkan lanjutkan proses berikutnya. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'contract.issue',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Contract Issue',
            'user_id': self.user_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.user_id.name} \n Penyelesaian Issue {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'contract.issue',
            'res_id': self.id,
        })
        notification.action_assign()
        self.write({ 'state': 'need_improvement' })

    def action_cancel(self):
        self.ensure_one()
        self.write({ 'state': 'cancel' })