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

    has_expense = fields.Selection(CATEGORY_SELECTION, string='Has Expense', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    expense_id = fields.Many2one('hr.expense', string='Expense')
    has_expense = fields.Selection(related='category_id.has_expense')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        
        for request in self:
            category_pr = self.env.ref('approvals_expense.approval_category_data_expense')
            if request.category_id.id == category_pr.id:
                if request.request_status == 'refused':
                    request.expense_id.sudo().action_need_improvement()
                elif request.request_status == 'approved':
                    request.expense_id.sudo().action_approved()

        return res
