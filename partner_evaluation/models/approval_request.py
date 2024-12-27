from odoo import _, api, fields, models


CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_evaluation_template = fields.Selection(CATEGORY_SELECTION, string='Has Evaluation Template', default='no')
    has_evaluation = fields.Selection(CATEGORY_SELECTION, string='Has Evaluation', default='no')

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    has_evaluation = fields.Selection(related='category_id.has_evaluation')
    evaluation_id = fields.Many2one('partner.evaluation', string='Evaluation')
    
    has_evaluation_template = fields.Selection(related='category_id.has_evaluation_template')
    template_id = fields.Many2one('evaluation.template', string='Template')

    @api.depends('approver_ids.status', 'approver_ids.required')
    def _compute_request_status(self):
        res = super(ApprovalRequest, self)._compute_request_status()
        
        for request in self:
            if request.category_id.id == self.env.ref('partner_evaluation.approval_category_data_evaluation').id:
                if request.request_status == 'refused':
                    request.evaluation_id.write({ 'state': 'refused' })
                elif request.request_status == 'approved':
                    request.purchase_request_id.write({ 'state': 'approved' })

        return res

