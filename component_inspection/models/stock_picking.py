from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    for_quality_check = fields.Boolean('For Quality Check')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('quality_check', 'Quality Check'), ('quality_pass', 'Quality Pass')], string='Status')
    approval_ids = fields.One2many('approval.inspection', 'picking_id', string='Approval')
    approval_count = fields.Integer('Approval Count', compute='_compute_approval_count')
    for_quality_check = fields.Boolean('For Quality Check', related='location_id.for_quality_check' )

    @api.depends('state')
    def _compute_show_validate(self):
        res = super()._compute_show_validate()
        for picking in self:
            if picking.state == 'quality_pass':
                picking.show_validate = True
        return res

    @api.depends('approval_ids')
    def _compute_approval_count(self):
        for record in self:
            record.approval_count = len(record.approval_ids)

    def action_show_inspection(self):
        self.ensure_one()
        if self.approval_count == 0:
            return
        action = self.env.ref('component_inspection.approval_inspection_action').sudo().read()[0]
        action['domain'] = [('picking_id', '=', self.id)]
        return action

    def generate_quality_check(self):
        for record in self:
            self.env['approval.inspection'].sudo().create({
                'picking_id': record.id,
                'state': 'draft',
                'user_id': self.env.user.id,
                'date': fields.Datetime.now(),
                'inspection_ids': [(0,0,{
                    'picking_id': record.id,
                    'move_id': move.id,
                    'category': record.picking_type_id.code,
                    'date': fields.Datetime.now(),
                    'user_id': self.env.user.id,
                    'state': 'draft',
                    'edition': record.approval_count+1,
                    'qty': move.product_uom_qty,
                    'product_id': move.product_id.id,
                }) for move in record.move_ids_without_package]
            })
            record.sudo().write({'state': 'quality_check'})

    def transfer_actual_stock(self):
        self.ensure_one()

    def button_validate(self):
        if not self.state == 'quality_pass' and self.for_quality_check:
            raise ValidationError("Product hasn't check by Quality Control!")
        return super(StockPicking, self).button_validate()


class StockMove(models.Model):
    _inherit = 'stock.move'

    state = fields.Selection(selection_add=[('quality_check', 'Quality Check')], string='Status')
    inspection_ids = fields.One2many('component.inspection', 'move_id', string='Inspection')
    inspection_count = fields.Integer('Inspection Count', compute='_compute_inspection_count')
    
    @api.depends('inspection_ids')
    def _compute_inspection_count(self):
        for record in self:
            record.inspection_count = len(record.inspection_ids)

