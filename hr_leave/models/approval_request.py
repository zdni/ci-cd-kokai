from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_hr_leave = fields.Selection(CATEGORY_SELECTION, string='Has Leave', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    hr_leave_id = fields.Many2one('hr.leave', string='Leave')
    has_hr_leave = fields.Selection(related='category_id.has_hr_leave')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('hr_leave.approval_category_data_hr_leave').id:
                if request.request_status == 'refused':
                    request.hr_leave_id.sudo().action_need_improvement()
                elif request.request_status == 'approved':
                    request.hr_leave_id.sudo().action_approved()
        return res