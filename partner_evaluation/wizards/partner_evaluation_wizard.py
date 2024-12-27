from odoo import _, api, fields, models

class PartnerEvaluationWizard(models.TransientModel):
    _name = 'partner.evaluation.wizard'
    _description = 'Wizard of Partner Evaluation'

    title = fields.Char('Title')
    evaluation_date = fields.Datetime('Evaluation Date')
    user_ids = fields.Many2many('res.users', string='Auditor', default=lambda self: [self.env.user.id])
    partner_id = fields.Many2one('res.partner', string='Partner')
    question_ids = fields.One2many('evaluation.question', 'evaluation_id', string='Question')
    conclusion = fields.Text('Conclusion')
    note = fields.Text('Note')


class EvaluationQuestion(models.TransientModel):
    _name = 'evaluation.question'
    _description = 'Question of Evaluation'

    evaluation_id = fields.Many2one('partner.evaluation.wizard', string='Evaluation')
    category_id = fields.Many2one('evaluation.category', string='Category')
    item_id = fields.Many2one('evaluation.item', string='Item Check', domain="[('category_id', '=', evaluation_id)]")
    remark = fields.Text('Remark')