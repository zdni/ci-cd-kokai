from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from datetime import datetime, timedelta


class MaintenanceStage(models.Model):
    _name = 'maintenance.stage'
    _description = 'Maintenance Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Maintenance Pipe')
    done = fields.Boolean('Request Done')


class MaintenanceOrder(models.Model):
    _name = 'maintenance.order'
    _description = 'Maintenance Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['maintenance.stage'].search([], limit=1)

    archive = fields.Boolean('Archive', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)

    stage_id = fields.Many2one('maintenance.stage', string='Stage', ondelete='restrict', tracking=True, group_expand='_read_group_stage_ids', default=_default_stage, copy=False)

    name = fields.Char('Subjects', required=True, tracking=True)
    request_date = fields.Datetime('Request Date', default=fields.Datetime.now(), tracking=True)
    request_by_id = fields.Many2one('res.users', string='Request By', default=lambda self: self.env.user.id)
    department_request_id = fields.Many2one('hr.department', string='Department Request', default=lambda self: self.env.user.department_id.id)
    description = fields.Text('Description', tracking=True)

    progressing_date = fields.Datetime('Progressing Date', tracking=True)
    expected_date = fields.Datetime('Expected Closing Date', tracking=True)
    duration = fields.Float('Duration', tracking=True)
    closing_date = fields.Datetime('Closing Date', tracking=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High'),
    ], string='Priority', default='0', required=True)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Ready for next Stage'),
    ], string='Kanban State', required=True, default='normal')

    def archive_maintenance_order(self):
        self.write({'archive': True})

    def reset_maintenance_order(self):
        """ Reinsert the maintenance request into the maintenance pipe in the first stage"""
        first_stage_obj = self.env['maintenance.stage'].search([], order="sequence asc", limit=1)
        # self.write({'active': True, 'stage_id': first_stage_obj.id})
        self.write({'archive': False, 'stage_id': first_stage_obj.id})

    def write(self, vals):
        for val in vals:
            if 'stage_id' in val:
                if val.get('stage_id') == self.env.ref('maintenance_order.maintenance_stage_data_draft').id:
                    val['closing_date'] = False
                if val.get('stage_id') == self.env.ref('maintenance_order.maintenance_stage_data_request').id:
                    val['request_date'] = fields.Datetime.now()
                if val.get('stage_id') == self.env.ref('maintenance_order.maintenance_stage_data_progress').id:
                    if self.department_id.id == self.env.user.department_id.id:
                        val['progressing_date'] = fields.Datetime.now()
                        val['responsible_id'] = self.env.user.id
                    else:
                        raise AccessDenied("You can't Set Stage to Progress")
                if val.get('stage_id') in [self.env.ref('maintenance_order.maintenance_stage_data_done').id, self.env.ref('maintenance_order.maintenance_stage_data_cancel').id]:
                    val['closing_date'] = fields.Datetime.now()
        return super(MaintenanceOrder, self).write(vals)

    @api.depends('progressing_date')
    def _compute_processing_time(self):
        for record in self:
            record.duration = 0
            record.expected_date = False
            if record.progressing_date:
                if record.expected_date:
                    record.duration = (record.expected_date - record.progressing_date).seconds/3600
                elif record.duration:
                    record.expected_date = record.progressing_date + timedelta(hours=record.duration)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
