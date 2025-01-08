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

                    attribute = self.env['product.attribute'].search([ ('id', '=', row_vals[0]) ])
                    if not attribute:
                        raise UserError(f"Attribute f{row_vals[0]} not Found")
                    
                    values = row_vals[1].split(" || ")
                    for value in values:
                        vals = {
                            'attribute_id': row_vals[0],
                            'name': value
                        }
                        try:
                            self.env['product.attribute.value'].create(vals)
                        except:
                            raise UserError(f"Can't create {value}")
        except UserError as e:
            raise UserError(str(e))