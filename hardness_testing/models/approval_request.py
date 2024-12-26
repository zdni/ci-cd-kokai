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

    has_hardness_testing = fields.Selection(CATEGORY_SELECTION, string='Has Hardness Testing', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    hardness_testing_id = fields.Many2one('hardness.testing', string='Hardness Testing')
    has_hardness_testing = fields.Selection(related='category_id.has_hardness_testing')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('hardness_testing.approval_category_data_hardness_testing').id:
                if request.request_status == 'refused':
                    request.hardness_testing_id.sudo().action_need_improvement()
                elif request.request_status == 'approved':
                    request.hardness_testing_id.sudo().action_approved()
        return res