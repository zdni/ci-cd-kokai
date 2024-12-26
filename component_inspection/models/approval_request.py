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

    has_component_inspection = fields.Selection(CATEGORY_SELECTION, string='Has Component Inspection', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    component_inspection_id = fields.Many2one('approval.inspection', string='Component Inspection')
    has_component_inspection = fields.Selection(related='category_id.has_component_inspection')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('component_inspection.approval_category_data_component_inspection').id:
                if request.request_status == 'refused':
                    request.component_inspection_id.sudo().action_need_improvement()
                elif request.request_status == 'approved':
                    request.component_inspection_id.sudo().action_approved()
        return res