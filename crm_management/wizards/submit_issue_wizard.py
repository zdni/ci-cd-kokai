from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class SubmitIssueWizard(models.TransientModel):
    _name = 'submit.issue.wizard'
    _description = 'Wizard for Submit Issue in FIR or FRK'

    ref_id = fields.Many2one('sale.order', string='Reference', required=True)
    description = fields.Text('Description', default='-')
    document = fields.Selection([
        ('inquiry', 'Inquiry'),
        ('contract', 'Contract'),
    ], string='Document', required=True, default='inquiry')
    approver_ids = fields.Many2many('res.users', string='Approver')

    def button_process(self):
        self.ensure_one()

        if self.ref_id:
            order = self.ref_id

            issue = {
                'name': 'New',
                'order_id': order.id,
                'lead_id': order.lead_id.id,
                'issue_date': fields.Datetime.now(),
                'description': self.description,
                'prepared_id': self.env.user.id,
                'approver_ids': [(0,0,self.approver_ids.ids)]
            }
            if self.document == 'inquiry':
                order.write({ 'inquiry_issue_ids': [(0, 0, issue)], 'inquiry_state': 'issue' })
            if self.document == 'contract':
                order.write({ 'contract_issue_ids': [(0, 0, issue)] })
        else:
            raise ValidationError("Submit Issue can't be Processed!")