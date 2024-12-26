from odoo import _, api, fields, models

class EvaluationCategory(models.Model):
    _name = 'evaluation.category'
    _description = 'Category of OHS Evaluation'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description', default='-')