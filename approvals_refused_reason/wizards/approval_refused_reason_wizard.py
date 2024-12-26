from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class ApprovalRefusedReasonWizard(models.TransientModel):
    _name = 'approval.refused.reason.wizard'
    _description = 'Wizard of Approval Refused Reason'

    request_id = fields.Many2one('approval.request', string='Request Doc')
    reason = fields.Text('Reason')

    def rejection_processed(self):
        self.ensure_one()

        request = self.request_id
        approver = request.mapped('approver_ids').filtered(lambda approver: approver.user_id == self.env.user)
        approver.write({'status': 'refused', 'reason': self.reason})
        request.sudo()._update_next_approvers('refused', approver, only_next_approver=False, cancel_activities=True)
        request.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()