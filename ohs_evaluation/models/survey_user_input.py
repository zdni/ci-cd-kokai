from odoo import _, api, fields, models

class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    evaluation_id = fields.Many2one('ohs.evaluation', string='Evaluation')
    nonconformity_id = fields.Many2one('nonconformity.report', string='Nonconformity')