import os
import base64, binascii, csv, io, tempfile, requests, xlrd
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class ImportProductAttribute(models.TransientModel):
    _name = 'import.product.attribute'
    _description = 'Import Product Attribute'

    file = fields.Binary('File Excel')
    is_create = fields.Boolean('Create when Value not Found?')

    def action_import(self):
        value_has_create = []
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

                    attribute = self.env['product.attribute'].search([ ('name', '=', row_vals[0]) ], limit=1)
                    if not attribute:
                        if self.is_create:
                            attribute = self.env['product.attribute'].create({
                                'name': row_vals[0],
                                'display_type': 'radio',
                                'create_variant': 'dynamic',
                            })
                        else:
                            raise UserError(f"Attribute {row_vals[0]} not Found")
                    
                    values = row_vals[1].split(" || ")
                    for value in values:
                        # check if value has created
                        has_created = self.env['product.attribute.value'].search([
                            ('attribute_id', '=', attribute.id),
                            ('name', '=', value),
                        ], limit=1)
                        if has_created:
                            value_has_create.append(f"{attribute.name} - {value}")
                            continue
                        vals = {
                            'attribute_id': attribute.id,
                            'name': value
                        }
                        try:
                            self.env['product.attribute.value'].create(vals)
                        except UserError as e:
                            raise UserError(f"Can't create {value}, \n {str(e)}")
        except UserError as e:
            raise UserError(str(e))
        
        # if len(value_has_create) > 0:
        #     raise UserError(f"Has Created: {' || '.join(value_has_create)}")