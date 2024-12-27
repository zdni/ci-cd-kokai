from odoo import _, api, fields, models

class EvaluationTemplate(models.Model):
    _name = 'evaluation.template'
    _description = 'Template of Evaluation Question'

    name = fields.Char('Title', required=True)
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    effective_date = fields.Date('Effective Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('used', 'Used'),
        ('expired', 'Expired'),
        ('cancel', 'Cancel'),
    ], string='State', default='draft')
    line_ids = fields.One2many('evaluation.question', 'template_id', string='Line')


class EvaluationQuestion(models.Model):
    _name = 'evaluation.question'
    _description = 'Question of Evaluation'

    template_id = fields.Many2one('evaluation.template', string='Template')
    category_id = fields.Many2one('evaluation.category', string='Category')


class EvaluationCategory(models.Model):
    _name = 'evaluation.category'
    _description = 'Category of Evaluation'

    name = fields.Char('Category', required=True, translate=True)
    item_ids = fields.One2many('evaluation.item', 'category_id', string='Questions')


class EvaluationItem(models.Model):
    _name = 'evaluation.item'
    _description = 'Item Check of Partner Evaluation'
    _order = 'category_id ASC, score DESC'

    category_id = fields.Many2one('evaluation.category', string='Category')
    name = fields.Char('Item Check', translate=True)
    score = fields.Integer('Score', default=1)