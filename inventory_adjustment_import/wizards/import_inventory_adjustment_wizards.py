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
                            raise UserError(f"Product {row_vals[1]}, Attribute {attribute_name}, f{product_attribute_value.name}, product_template_variant_value_ids not Found")
                        value_ids.append(product_template_variant_value_ids.id)

                    product = False
                    product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', product_tmpl_id.id),
                        ('product_template_attribute_value_ids', '=', value_ids),
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

                    lot = self.env['stock.lot'].search([
                        ('name', '=', row_vals[4]),
                        ('product_id', '=', product.id),
                        ('company_id', '=', self.env.company.id),
                    ])
                    if not lot:
                        lot = self.env['stock.lot'].create({
                            'name': row_vals[4],
                            'product_id': product.id,
                            'company_id': self.env.company.id,
                        })

                    vals = {
                        'location_id': location.id,
                        'product_id': product.id,
                        'lot_id': lot.id,
                        'product_uom_id': product.uom_id.id,
                        'inventory_date': row_vals[7],
                    }
                    quant = self.env['stock.quant'].create(vals)
                    quant.write({ 'inventory_quantity': int(row_vals[5]) })
                    quant.action_set_inventory_quantity()
                    quant.action_apply_inventory()

        except UserError as e:
            raise UserError(str(e))
