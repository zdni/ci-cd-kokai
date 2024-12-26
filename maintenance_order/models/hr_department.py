from odoo import _, api, fields, models


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    maintenance_request_ids = fields.One2many('maintenance.order', 'department_request_id', string='Maintenance Request')
    maintenance_request_count = fields.Integer('Maintenance Request Count', compute='_compute_maintenance_request_count')
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_request_count(self):
        for record in self:
            record.maintenance_request_count = len(record.maintenance_request_ids)

    def action_show_maintenance_request(self):
        self.ensure_one()
        if self.maintenance_request_count == 0:
            return
        action = self.env.ref('maintenance_order.maintenance_order_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.maintenance_request_ids.ids)]
        return action

    maintenance_task_ids = fields.One2many('maintenance.order', 'department_id', string='Maintenance Task')
    maintenance_task_count = fields.Integer('Maintenance Task Count', compute='_compute_maintenance_task_count')
    @api.depends('maintenance_task_ids')
    def _compute_maintenance_task_count(self):
        for record in self:
            record.maintenance_task_count = len(record.maintenance_task_ids)

    def action_show_maintenance_task(self):
        self.ensure_one()
        if self.maintenance_task_count == 0:
            return
        action = self.env.ref('maintenance_order.maintenance_order_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.maintenance_task_ids.ids)]
        return action