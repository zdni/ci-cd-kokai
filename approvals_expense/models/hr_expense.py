from odoo import _, api, fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    team_id = fields.Many2one('department.team', string='Team')
    state = fields.Selection(selection_add=[('request', 'Request'), ('need_improvement', 'Need Improvement')], string='Status')
    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='expense_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def _send_notification_to_team(self):
        self.ensure_one()
        if self.team_id:
            schedule = self.env['assignment.task'].sudo().create({
                'department_ids': [self.team_id.department_id.id],
                'user_id': self.env.user.id,
                'user_ids': self.team_id.member_ids,
                'assigned_to': 'employee',
                'subject': f"Notifikasi Request Expense {self.name}",
                'description': f"Notifikasi Request Expense {self.name}",
                'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
                'model': 'hr.expense',
                'res_id': self.id,
            })
            schedule.action_assign()

    def generate_approval_request(self):
        self.ensure_one()
        self._send_notification_to_team()
        category_pr = self.env.ref('approvals_expense.approval_category_data_expense')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'expense_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.employee_id.name} \n {self.description}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'request'
        })
        request = self.approval_ids[self.approval_count-1]
        approver = self.env['approval.approver'].search([
            ('request_id.id', '=', request.id),
            ('user_id.id', '=', 2),
        ])
        if approver:
            approver.sudo().write({ 'user_id': self.employee_id.parent_id.user_id.id })
        request.action_confirm()

    def action_view_approval_request(self):
        action = (self.env.ref('approvals.approval_request_action_all').sudo().read()[0])
        approvals = self.mapped('approval_ids')
        if len(approvals) > 1:
            action['domain'] = [('id', 'in', approvals.ids)]
        elif approvals:
            action['views'] = [(self.env.ref('approvals.approval_request_view_form').id, 'form')]
            action['res_id'] = approvals.ids[0]
        return action

    def action_approved(self):
        self.ensure_one()
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approve Expense',
            'user_id': self.employee_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.employee_id.name} \n Expense {self.name} yang diajukan telah disetujui. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.expense',
            'res_id': self.id,
        })
        self.action_submit_expenses()
        self.sheet_id.write({ 'state': 'approve' })
        # self.sheet_id.write({ 'user_id': self.env.user.id })
        # self.sheet_id.action_submit_sheet()
        # self.sheet_id.approve_expense_sheets()
        notification.action_assign()
        self.write({ 'state': 'approved' })

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Expense',
            'user_id': self.employee_id.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.employee_id.name} \n Expense {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'hr.expense',
            'res_id': self.id,
        })
        notification.action_assign()
    