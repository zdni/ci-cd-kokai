from odoo import _, api, fields, models
from odoo.exceptions import UserError

class IRSequenceDepartment(models.Model):
    _name = 'ir.sequence.department'
    _description = 'Sequence for Each Department'

    model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', required=True)

class IRSequence(models.Model):
    _inherit = 'ir.sequence'

    department_id = fields.Many2one('hr.department', string='Department')

class HRDepartment(models.Model):
    _inherit = 'hr.department'

    sequence_ids = fields.One2many('ir.sequence.department', 'department_id', string='Sequence')
    alias = fields.Char('Alias')
    
    def action_generate_sequence_wizard(self):
        if not self.alias:
            raise UserError('Please Set Alias for Department First!')
        
        ctx = dict(default_department_id=self.id, active_ids=self.ids)
        return {
            'name': _('Generate Sequence'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'generate.sequence.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    activities_ids = fields.One2many('department.activity', 'department_id', string='Activities')
    activities_count = fields.Integer('Activities Count', compute='_compute_activities_count')

    @api.depends('activities_ids')
    def _compute_activities_count(self):
        for record in self:
            record.activities_count = len(record.activities_ids)

    def action_show_activities(self):
        self.ensure_one()
        action = self.env.ref('department_detail.department_activity_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.activities_ids.ids)]
        action['context'] = {'default_department_id': self.id}
        return action

    shift_ids = fields.One2many('schedule.shift', 'department_id', string='Shift')


class ScheduleShift(models.Model):
    _name = 'schedule.shift'
    _description = 'Schedule Shift'

    department_id = fields.Many2one('hr.department', string='Department', ondelete='cascade')
    name = fields.Char('Shift', compute='_compute_name')
    description = fields.Char('Shift', required=True)
    start_time = fields.Float('Start Time', default=8.0)
    end_time = fields.Float('End Time', default=16.5)

    @api.depends('description', 'start_time', 'end_time')
    def _compute_name(self):
        for record in self:
            start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(record.start_time * 60, 60))
            end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(record.end_time * 60, 60))
            record.name = f"{record.description} || {start_time} - {end_time}"