from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_critical = fields.Boolean('Is Critical')
    part_id = fields.Many2one('product.part', string='Part')
    # dimension_ids = fields.One2many('product.dimension', 'product_id', string='Dimension')

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_critical = fields.Boolean('Is Critical', related='product_tmpl_id.is_critical')
    part_id = fields.Many2one('product.part', string='Part', related='product_tmpl_id.part_id')
    weight = fields.Float('Weight (Kg)')
    # specification_ids = fields.One2many('product.specification', 'product_id', string='Specification')
    # material_id = fields.Many2one('bill.of.material', string='BoM')
    # dimension_ids = fields.One2many('product.dimension', 'product_id', string='Dimension')

class ProductDimension(models.Model):
    _name = 'product.dimension'
    _description = 'Product Dimension'

    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product', related='product_id.product_tmpl_id')
    name = fields.Char('Name', required=True)
    min = fields.Float('Min')
    max = fields.Float('Max')


class ProductSpecification(models.Model):
    _name = 'product.specification'
    _description = 'Product Specification'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product', string='Product', required=True)
    type_id = fields.Many2one('manufacturing.type', string='Manufacturing', tracking=True)
    manufacturing_ids = fields.Many2many('standard.manufacturing', string='Value', domain="[('type_id', '=', type_id)]", tracking=True)


class ProductDrawing(models.Model):
    _name = 'product.drawing'
    _description = 'Product Drawing'

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', string='Product Template', related='product_id.product_tmpl_id')
    attachment_id = fields.Many2one('ir.attachment', string='File')