from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tensile_ids = fields.One2many('tensile.testing', 'picking_id', string='Tensile')
    tensile_count = fields.Integer('Tensile Count', compute='_compute_tensile_count')
    @api.depends('tensile_ids')
    def _compute_tensile_count(self):
        for record in self:
            record.tensile_count = len(record.tensile_ids)

    def action_show_tensile(self):
        self.ensure_one()
        if self.tensile_count == 0:
            return
        action = self.env.ref('tensile_testing.tensile_testing_action').sudo().read()[0]
        action['domain'] = [('id', 'in', self.tensile_ids.ids)]
        return action

    def generate_quality_check(self):
        res = super(StockPicking, self).generate_quality_check()
        for record in self:
            for move in record.move_ids_without_package:
                self.env['tensile.testing'].sudo().create({
                    'picking_id': record.id,
                    'product_id': move.product_id.id,
                    'move_id': move.id,
                })
        return res
