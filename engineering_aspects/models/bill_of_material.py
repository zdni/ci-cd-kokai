from odoo import _, api, fields, models


class BillOfMaterial(models.Model):
    _name = 'bill.of.material'
    _description = 'Bill Of Material'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', default='New')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float('Qty', default=1)
    orderline_ids = fields.One2many('sale.order.line', 'material_id', string='Order Line')
    part_ids = fields.One2many('material.line', 'material_id', string='Parts')


class MaterialLine(models.Model):
    _name = 'material.line'
    _description = 'Material Line'

    material_id = fields.Many2one('bill.of.material', string='Material', required=True)
    part_id = fields.Many2one('product.part', string='Part')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    init_qty = fields.Float('Qty/Pcs', default=1)
    total_qty = fields.Float('Required Qty', compute='_compute_total_qty')
    category_id = fields.Many2one('product.category', string='Category', related='product_id.categ_id')

    @api.depends('init_qty')
    def _compute_total_qty(self):
        for record in self:
            record.sudo().total_qty = record.init_qty*record.material_id.qty


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    material_id = fields.Many2one('bill.of.material', string='Material')
