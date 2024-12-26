from odoo import _, api, fields, models


class HRWorkArea(models.Model):
    _name = 'hr.work.area'
    _description = 'HR Work Area'

    name = fields.Char('Display Name', compute='_compute_name', translate=True)
    location_id = fields.Many2one('hr.work.location', string='Location', ondelete='cascade', required=True)
    display_name = fields.Char('Name', translate=True)

    @api.depends('display_name', 'location_id')
    def _compute_name(self):
        for record in self:
            record.sudo().name = f"{record.display_name or 'Area'} - {record.location_id.name or 'Location'}"

class HRWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    area_ids = fields.One2many('hr.work.area', 'location_id', string='Area')
    area_count = fields.Integer('Area Count', compute="_compute_area_count")

    @api.depends('area_ids')
    def _compute_area_count(self):
        for record in self:
            record.sudo().area_count = len(record.area_ids)

    def action_show_work_area(self):
        self.ensure_one()
        if self.sudo().area_count == 0:
            return
        
        action = self.env.ref('hr_work_area_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.area_ids.id)]
        return action