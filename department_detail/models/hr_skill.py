from odoo import _, api, fields, models


class HRSkill(models.Model):
    _name = 'hr.skill'
    _description = 'Hr Skill'

    name = fields.Char('Name', required=True)
    job_id = fields.Many2one('hr.job', string='Job')
    level = fields.Selection([
        ('novice', 'Novice'),
        ('competent', 'Competent'),
        ('proficient', 'Proficient'),
        ('expert', 'Expert'),
        ('master', 'Master'),
    ], string='Level', default='novice', required=True)
    description = fields.Char('Description')


class HRJob(models.Model):
    _inherit = 'hr.job'

    skill_ids = fields.One2many('hr.skill', 'job_id', string='Skill')


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    employee_type_id = fields.Many2one('hr.contract.type', string='Employee Type', related='job_id.contract_type_id')