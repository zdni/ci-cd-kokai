from odoo import _, api, fields, models
import base64, binascii, csv, io, tempfile, requests, xlrd
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class ImportInventoryAdjustmentWizard(models.TransientModel):
    _name = 'import.inventory.adjustment.wizard'
    _description = 'Import Inventory Adjustment Wizard'

    file = fields.Binary('File Excel')
    check = fields.Selection([
        ('all', 'All'),
        ('location', 'Location'),
        ('template', 'Product Template'),
        ('attribute', 'Product Attribute'),
        ('variant', 'Product Variant'),
    ], string='Check', default='all')

    def checking_value(self):
        try:
            try:
                file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file_pointer.write(binascii.a2b_base64(self.file))
                file_pointer.seek(0)
                workbook = xlrd.open_workbook(file_pointer.name)
                sheet = workbook.sheet_by_index(0)
            except:
                raise UserError(_("File not Valid"))
            error = {}
            if self.check == 'all':
                error = {
                    'Location': '',
                    'Product Template': '',
                    'Attribute': '',
                    'Product Attribute': '',
                    'Variant': '',
                    'Product Variant': '',
                }
            if self.check == 'location':
                error['Location'] = ''
            if self.check == 'template':
                error['Product Template'] = ''
            if self.check == 'attribute':
                error['Attribute'] = ''
                error['Product Attribute'] = ''
            if self.check == 'variant':
                error['Variant'] = ''
                error['Product Variant'] = ''

            i = 0
            for rec in range(sheet.nrows):
                i += 1
                if rec >= 1:
                    _logger.warning(i)
                    row_vals = sheet.row_values(rec)
                    if len(row_vals) < int(2):
                        raise UserError(_("Please ensure that you selected the correct file"))

                    if self.check in ['all', 'location']:
                        location = self.env['stock.location'].search([
                            ('complete_name', '=', row_vals[0]),
                            ('company_id', '=', self.env.company.id)
                        ], limit=1)
                        if not location:
                            error['Location'] += f"{i}) {row_vals[0]} || "
                    
                    product_tmpl_id = self.env['product.template'].search([ ('name', '=', row_vals[1]) ], limit=1)
                    if not product_tmpl_id and self.check in ['all', 'template']:
                        error['Product Template'] += f"{i}) {row_vals[1]} || "

                    if self.check in ['all', 'attribute', 'variant']:
                        variants = row_vals[3].split(' || ')
                        for variant in variants:
                            attribute_name = variant.split(': ')[0]
                            variant_name = variant.split(': ')[1]
                            attribute = self.env['product.attribute'].search([ ('name', '=', attribute_name) ], limit=1)
                            if not attribute and self.check in ['all', 'attribute']:
                                error['Attribute'] += f"{i}) {attribute_name} || "
                            
                            product_tmpl_attr = self.env['product.template.attribute.line'].search([
                                ('product_tmpl_id', '=', product_tmpl_id.id),
                                ('attribute_id', '=', attribute.id),
                            ])
                            if not product_tmpl_attr and self.check in ['all', 'attribute']:
                                error['Product Attribute'] += f"{i}) {row_vals[1]} - {attribute_name} || "

                            product_attribute_value = self.env['product.attribute.value'].search([ ('name', '=', variant_name), ('attribute_id', '=', attribute.id) ], limit=1)
                            if not product_attribute_value and self.check in ['all', 'variant']:
                                error['Variant'] += f"{i}) {attribute.name} - {variant_name} || "

                            product_template_variant_value_ids = self.env['product.template.attribute.value'].search([
                                ('attribute_id', '=', attribute.id),
                                ('product_attribute_value_id', '=', product_attribute_value.id),
                                ('product_tmpl_id', '=', product_tmpl_id.id),
                                ('attribute_line_id', '=', product_tmpl_attr.id),
                            ], limit=1)
                            if not product_template_variant_value_ids and self.check in ['all', 'variant']:
                                error['Product Variant'] += f"{i}) {row_vals[1]} - {attribute_name} - {product_attribute_value.name} || "
            raise UserError(str(error))
        except UserError as e:
            raise UserError(str(e))
        

    def action_import(self):
        try:
            try:
                file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file_pointer.write(binascii.a2b_base64(self.file))
                file_pointer.seek(0)
                workbook = xlrd.open_workbook(file_pointer.name)
                sheet = workbook.sheet_by_index(0)
            except:
                raise UserError(_("File not Valid"))

            for rec in range(sheet.nrows):
                if rec >= 1:
                    row_vals = sheet.row_values(rec)
                    if len(row_vals) < int(2):
                        raise UserError(_("Please ensure that you selected the correct file"))

                    location = self.env['stock.location'].search([
                        ('complete_name', '=', row_vals[0]),
                        ('company_id', '=', self.env.company.id)
                    ], limit=1)
                    if not location:
                        raise UserError(f"Location {row_vals[0]} in {self.env.company.name} not Found")

                    product_tmpl_id = self.env['product.template'].search([ ('name', '=', row_vals[1]) ], limit=1)
                    if not product_tmpl_id:
                        raise UserError(_(f"Product {row_vals[1]} not Found"))

                    value_ids = []
                    value_str_ids = []
                    variants = row_vals[3].split(' || ')
                    for variant in variants:
                        attribute_name = variant.split(': ')[0]
                        variant_name = variant.split(': ')[1]
                        attribute = self.env['product.attribute'].search([ ('name', '=', attribute_name) ], limit=1)
                        if not attribute:
                            raise UserError(_(f"Product {row_vals[1]}, Attribute {attribute_name} not Found"))
                        
                        product_tmpl_attr = self.env['product.template.attribute.line'].search([
                            ('product_tmpl_id', '=', product_tmpl_id.id),
                            ('attribute_id', '=', attribute.id),
                        ])
                        if not product_tmpl_attr:
                            raise UserError(f"Product {row_vals[1]} don't have attribute {attribute_name}")
                        product_attribute_value = self.env['product.attribute.value'].search([ ('name', '=', variant_name), ('attribute_id', '=', attribute.id) ], limit=1)
                        if not product_attribute_value:
                            raise UserError(f"Product {row_vals[1]}, Attribute {attribute_name}, Variant {variant_name} not Found")

                        product_template_variant_value_ids = self.env['product.template.attribute.value'].search([
                            ('attribute_id', '=', attribute.id),
                            ('product_attribute_value_id', '=', product_attribute_value.id),
                            ('product_tmpl_id', '=', product_tmpl_id.id),
                            ('attribute_line_id', '=', product_tmpl_attr.id),
                        ], limit=1)
                        if not product_template_variant_value_ids:
                            raise UserError(f"Product {row_vals[1]}, Attribute {attribute_name}, {product_attribute_value.name}, product_template_variant_value_ids not Found")
                        value_ids.append(product_template_variant_value_ids.id)
                        value_str_ids.append(str(product_template_variant_value_ids.id))
                        value_ids.sort()

                    product = False
                    product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', product_tmpl_id.id),
                        ('combination_indices', '=', ','.join(f"{i}" for i in value_ids)),
                    ], limit=1)
                    if not product:
                        vals = {
                            'name': row_vals[2],
                            'product_tmpl_id': product_tmpl_id.id,
                            'product_template_attribute_value_ids': [(6, 0, value_ids)],
                        }
                        product = self.env['product.product'].create(vals)

                    if not product:
                        raise UserError(f"Can't create {row_vals[2]}")

                    lot_id = ''
                    if row_vals[4] != '':
                        lot_id = self.env['stock.lot'].search([
                            ('name', '=', row_vals[4]),
                            ('product_id', '=', product.id),
                            ('company_id', '=', self.env.company.id),
                        ], limit=1).id

                    if not lot_id:
                        lot_id = self.env['stock.lot'].create({
                            'name': row_vals[4],
                            'product_id': product.id,
                            'company_id': self.env.company.id,
                        }).id
                    
                    if product.tracking == 'lot':
                        lot_id = '' # generate lot
                    
                    vals = {
                        'location_id': location.id,
                        'product_id': product.id,
                        'lot_id': lot_id,
                        'product_uom_id': product.uom_id.id,
                        'inventory_date': row_vals[7],
                    }
                    if product.tracking == 'serial':
                        for i in range(0, int(row_vals[5])):
                            self.create_inventory_adjustment(1, vals)
                    else:
                        self.create_inventory_adjustment(int(row_vals[5]), vals)
                    self.create_inventory_adjustment(int(row_vals[5]), vals)


        except UserError as e:
            raise UserError(str(e))

    def create_inventory_adjustment(self, qty, vals):
        quant = self.env['stock.quant'].create(vals)
        quant.write({ 'inventory_quantity': qty })
        quant.action_set_inventory_quantity()
        quant.action_apply_inventory()