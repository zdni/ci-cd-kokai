from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    hardness_ids = fields.One2many('hardness.testing', 'picking_id', string='Hardness')
    hardness_count = fields.Integer('Hardness Count', compute='_compute_hardness_count')
    @api.depends('hardness_ids')
    def _compute_hardness_count(self):
        for record in self:
            record.hardness_count = len(record.hardness_ids)

    def action_show_hardness(self):
        self.ensure_one()
        if self.hardness_count == 0:
            return
        action = self.env.ref('hardness_testing.hardness_testing_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.hardness_ids.ids)]
        return action

    def generate_quality_check(self):
        res = super(StockPicking, self).generate_quality_check()
        for record in self:
            self.env['hardness.testing'].sudo().create({
                'picking_id': record.id,
                'line_ids': [(0,0,{
                    'product_id': move.product_id.id,
                    'move_id': move.id,
                }) for move in record.move_ids_without_package]
            })
        return res
