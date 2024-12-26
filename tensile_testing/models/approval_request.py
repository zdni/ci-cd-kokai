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

    has_tensile_testing = fields.Selection(CATEGORY_SELECTION, string='Has Tensile Testing', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    tensile_testing_id = fields.Many2one('approval.inspection', string='Tensile Testing')
    has_tensile_testing = fields.Selection(related='category_id.has_tensile_testing')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('tensile_testing.approval_category_data_tensile_testing').id:
                if request.request_status == 'refused':
                    request.tensile_testing_id.sudo().write({ 'state': 'need_improvement' })
                elif request.request_status == 'approved':
                    request.tensile_testing_id.sudo().action_approved()
        return res