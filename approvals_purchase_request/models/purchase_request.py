from odoo import _, api, Command, fields, models
import logging

_logger = logging.getLogger(__name__)

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    approval_ids = fields.One2many(comodel_name='approval.request', inverse_name='purchase_request_id', string='Approval Request', readonly=True, copy=False, tracking=True)
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count', readonly=True)
    state = fields.Selection(selection_add=[ ('need_improvement', 'Need Improvement') ], ondelete={'need_improvement': 'cascade'})

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for rec in self:
            rec.approval_count = len(rec.mapped('approval_ids'))

    def generate_approval_request(self):
        self.ensure_one()

        category_pr = self.env.ref('approvals_purchase_request.approval_category_data_purchase_request')
        vals = {
            'name': 'Request Approval for ' + self.name,
            'purchase_request_id': self.id,
            'request_owner_id': self.env.user.id,
            'category_id': category_pr.id,
            'reason': f"Request Approval for {self.name} from {self.requested_by.name} \n {self.description}"
        }
        self.sudo().write({
            'approval_ids': [(0, 0, vals)],
            'state': 'to_approve'
        })
        
        request = self.approval_ids[self.approval_count-1]
        approver = self.env['approval.approver'].search([
            ('request_id.id', '=', request.id),
            ('user_id.id', '=', 2),
        ])
        if approver:
            approver.sudo().write({ 'user_id': self.approver_id.id })
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
        self.write({ 'state': 'approved' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Approve Purchase Request',
            'user_id': self.requested_by.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by.name} \n Purchase Request {self.name} yang diajukan telah disetujui. Silahkan lanjutkan proses permintaan kepada Tim Purchasing dengan menekan tombol Action 'In Progress'. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.request',
            'res_id': self.id,
        })
        notification.action_assign()

    def action_need_improvement(self):
        self.ensure_one()
        self.write({ 'state': 'need_improvement' })
        notification = self.env['schedule.task'].sudo().create({
            'company_id': self.env.company.id,
            'subject': 'Notifikasi Refused Purchase Request',
            'user_id': self.requested_by.id,
            'assign_by_id': 1,
            'schedule_type_id': self.env.ref('schedule_task.mail_activity_type_data_notification').id,
            'description': f"Kepada {self.requested_by.name} \n Purchase Request {self.name} yang diajukan ditolak. Silahkan ditinjau kembali dan diperbaiki sesuai dengan catatan penolakan yang telah dicantumkan. \n Terima Kasih",
            'date': fields.Date.today(),
            'start_date': fields.Datetime.now(),
            'stop_date': fields.Datetime.now(),
            'state': 'draft',
            'type': 'notification',
            'model': 'purchase.request',
            'res_id': self.id,
        })
        notification.action_assign()