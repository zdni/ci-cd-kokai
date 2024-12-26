from odoo import _, api, fields, models

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_work_accident = fields.Selection(CATEGORY_SELECTION, string='Has WOrk Accident', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    accident_id = fields.Many2one('work.accident', string='Accident')
    has_work_accident = fields.Selection(related='category_id.has_work_accident')
    
    @api.model_create_multi
    def create(self, vals):
        approvals = super(ApprovalRequest, self).create(vals)
        for approval in approvals:
            approval.doc_number = approval.accident_id.name
            approval.reason = ''
        return approvals

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        
        for request in self:
            category_pr = self.env.ref('work_accident.approval_category_data_work_accident')
            if request.category_id.id == category_pr.id:
                if request.request_status == 'refused':
                    request.accident_id.write({ 'state': 'need_improvement' })
                elif request.request_status == 'approved':
                    request.accident_id.write({ 'state': 'approved' })
        return res