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

    has_report_summary_cpar = fields.Selection(CATEGORY_SELECTION, string='Has Report Summary CPAR', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    report_summary_cpar_id = fields.Many2one('report.summary.cpar', string='Report Summary CPAR')
    has_report_summary_cpar = fields.Selection(related='category_id.has_report_summary_cpar')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            if request.category_id.id == self.env.ref('corrective_preventive_action.approval_category_data_report_summary_cpar').id:
                if request.request_status == 'refused':
                    request.report_summary_cpar_id.sudo().action_refused()
                elif request.request_status == 'approved':
                    request.report_summary_cpar_id.sudo().action_approved()
        return res