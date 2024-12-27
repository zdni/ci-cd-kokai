from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class GenerateEvaluationWizard(models.TransientModel):
    _name = 'generate.evaluation.wizard'
    _description = 'Generate Evaluation for Partner'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    template_id = fields.Many2one('evaluation.template', string='Template', required=True)
    user_ids = fields.Many2many('res.users', string='Auditor', default=lambda self: [self.env.user.id], required=True)

    def button_process(self):
        self.ensure_one()

        partner = self.partner_id

        if not partner:
            raise ValidationError("Can't Generate Evaluation! Please Contact Administrator!")

        partner.write({ 
            'evaluation': 'process', 
            'evaluation_ids': [(0,0,{
                'template_id': self.template_id.id,
                'name': 'New',
                'user_id': self.user_id.id,
            })]
        })
        partner.action_show_partner_evaluation()

