from odoo import _, api, fields, models

class NonconformityReport(models.Model):
    _name = 'nonconformity.report'

    evaluation_id = fields.Many2one('ohs.evaluation', string='Evaluation')
    line_id = fields.Many2one('survey.user_input.line', string='Line', required=True)
    code = fields.Char('Code', default='New', required=True)
    inspector_id = fields.Many2one('res.users', string='Inspector', required=True)
    pic_id = fields.Many2one('res.users', string='PIC', required=True)
    date_of_issue = fields.Datetime('Date Of Issue', required=True)
    category_id = fields.Many2one('evaluation.category', string='Source')
    # source = fields.Selection([
    #     ('ia', 'Internal Audit'),
    #     ('ea', 'External Audit'),
    #     ('si', 'System Incompatibility'),
    #     ('mr', 'Management Review'),
    #     ('in', 'Inspection'),
    #     ('sop', 'SOP'),
    #     ('rr', 'Rules/Requirements'),
    #     ('other', 'Others'),
    # ], string='Source', default='in', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('process', 'Process'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel'),
    ], string='State', default='new', required=True)
    # findings
    description = fields.Html('Description of Nonconformity')
    completion_date = fields.Date('Completion Date')
    # accept
    # inspector_accept = fields.Boolean('Inspector Accept')
    suggestion_line_ids = fields.One2many('suggestion.nonconformity', 'nonconformity_id', string='Suggestion Line')
    root_cause_ids = fields.One2many('root_cause.nonconformity', 'nonconformity_id', string='Root Cause Line')
    correction_action_ids = fields.One2many('corrective.action', 'nonconformity_id', string='Corrective Action Line')
    preventive_measure_ids = fields.One2many('preventive.measure', 'nonconformity_id', string='Preventive Measure Line')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val['name'] == 'New':
                val['name'] = self.env['ir.sequence'].next_by_code('non_conformity.report')
        return super(NonconformityReport, self).create(vals)

class SuggestionNonconformity(models.Model):
    _name = 'suggestion.nonconformity'

    nonconformity_id = fields.Many2one('nonconformity.report', string='Nonconformity Ref')
    suggestion = fields.Char('Suggestion', required=True)


class RootCauseNonconformity(models.Model):
    _name = 'root_cause.nonconformity'

    nonconformity_id = fields.Many2one('nonconformity.report', string='Nonconformity Ref')
    root_cause = fields.Char('Root Cause', required=True)

class CorrectiveAction(models.Model):
    _name = 'corrective.action'

    nonconformity_id = fields.Many2one('nonconformity.report', string='Nonconformity Ref')
    corrective = fields.Char('Corrective', required=True)
    pic_id = fields.Many2one('res.users', string='PIC')
    due_date = fields.Date('Due Date')
    completion_date = fields.Date('Completion Date')

class PreventiveMeasure(models.Model):
    _name = 'preventive.measure'

    nonconformity_id = fields.Many2one('nonconformity.report', string='Nonconformity Ref')
    prevention = fields.Char('Prevention', required=True)
    pic_id = fields.Many2one('res.users', string='PIC')
