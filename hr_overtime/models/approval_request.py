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

    has_hr_overtime = fields.Selection(CATEGORY_SELECTION, string='Has Overtime', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    hr_overtime_id = fields.Many2one('hr.overtime', string='Overtime')
    has_hr_overtime = fields.Selection(related='category_id.has_hr_overtime')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('hr_overtime.approval_category_data_hr_overtime').id:
                if request.request_status == 'refused':
                    request.hr_overtime_id.sudo().action_need_improvement()
                elif request.request_status == 'approved':
                    request.hr_overtime_id.sudo().action_approved()
        return res