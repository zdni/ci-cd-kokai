from odoo import _, api, fields, models

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_contract_issue = fields.Selection(CATEGORY_SELECTION, string='Has Contract Issue', default='no')
    has_contract_review = fields.Selection(CATEGORY_SELECTION, string='Has Contract Review', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    issue_id = fields.Many2one('contract.issue', string='Issue')
    has_contract_issue = fields.Selection(related='category_id.has_contract_issue')
    
    order_id = fields.Many2one('sale.order', string='Doc Ref')
    has_contract_review = fields.Selection(related='category_id.has_contract_review')
    
    @api.model_create_multi
    def create(self, vals):
        approvals = super(ApprovalRequest, self).create(vals)
        for approval in approvals:
            if approval.issue_id or approval.order_id:
                approval.doc_number = approval.order_id.name if approval.order_id else approval.issue_id.name
            approval.reason = ''
        return approvals

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        for request in self:
            category_pr = self.env.ref('crm_management.approval_category_data_contract_issue')
            if request.category_id.id == category_pr.id:
                if request.request_status == 'refused':
                    request.issue_id.action_need_improvement()
                elif request.request_status == 'approved':
                    request.issue_id.action_approved()

            category_pr = self.env.ref('crm_management.approval_category_data_contract_review')
            if request.category_id.id == category_pr.id:
                if request.request_status == 'refused':
                    request.order_id.action_need_improvement()
                elif request.request_status == 'approved':
                    request.order_id.action_approved()

        return res