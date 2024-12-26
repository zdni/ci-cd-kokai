from odoo import _, api, fields, models

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    part_ids = fields.One2many('equipment.part', 'employee_id', string='Equipment')
    equipment_count = fields.Integer('Equipment Count', compute='_compute_equipment_count', default=0)
    equipment_ids = fields.One2many('stock.equipment', 'employee_id', string='Equipment')
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.sudo().equipment_count = len(record.equipment_ids)

    def action_show_stock_equipment(self):
        self.ensure_one()
        if len(self.equipment_count) == 0:
            return
        equipments = self.mapped('equipment_ids')
        action = self.env.ref('employee_inventory.stock_equipment_action').sudo().read()[0]
        action['domain'] = [('id', 'in', equipments.ids)]
        return action


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    part_ids = fields.One2many('equipment.part', 'department_id', string='Equipment')
    equipment_ids = fields.One2many('stock.equipment', 'department_id', string='Equipment')
    equipment_count = fields.Integer('Equipment Count', compute='_compute_equipment_count', default=0)
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for record in self:
            record.sudo().equipment_count = len(record.equipment_ids)

    def action_show_stock_equipment(self):
        self.ensure_one()
        if len(self.equipment_count) == 0:
            return
        equipments = self.mapped('equipment_ids')
        action = self.env.ref('employee_inventory.stock_equipment_action').sudo().read()[0]
        action['domain'] = [('id', 'in', equipments.ids)]

