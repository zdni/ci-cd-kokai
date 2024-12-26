from odoo import _, api, fields, models

class ReturnedEquipmentWizard(models.TransientModel):
    _name = 'returned.equipment.wizard'
    _description = 'Wizard for Returned Equipment Used by Employee'

    returned_time = fields.Datetime('Returned Time', default=fields.Datetime.now())
    equipment_id = fields.Many2one('stock.equipment', string='Equipment', required=True)
    line_ids = fields.One2many('returned.line.wizard', 'doc_id', string='Line')

class ReturnedLine(models.TransientModel):
    _name = 'returned.line.wizard'
    _description = 'Line of Returned Equipment'

    doc_id = fields.Many2one('returned.equipment.wizard', string='Doc Ref', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float('Qty')
    uom_id = fields.Many2one('uom.uom', string='UoM')
    part_id = fields.Many2one('equipment.part', string='Part ID')
    lot_ids = fields.Many2many('stock.lot', string='Serial Numbers', domain="[('product_id', '=', product_id)]")