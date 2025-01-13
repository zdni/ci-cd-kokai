import os
import base64, binascii, csv, io, tempfile, requests, xlrd
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class ImportProductTemplate(models.TransientModel):
    _name = 'import.product.template'
    _description = 'Import Product Template'

    file = fields.Binary('File Excel')

    def action_import(self):
        PRODUCT_TYPE = {
            'Consumable': 'consu',
            'Service': 'service',
            'Storable Product': 'product',
        }
        try:
            try:
                file_pointer = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                file_pointer.write(binascii.a2b_base64(self.file))
                file_pointer.seek(0)
                workbook = xlrd.open_workbook(file_pointer.name)
                sheet = workbook.sheet_by_index(0)
            except:
                raise UserError(_("File not Valid"))
            
            name = ''
            categ_id = False
            uom_id = False
            attribute_line_ids = []
            
            vals = {}
            for rec in range(sheet.nrows):
                if rec >= 1:
                    row_vals = sheet.row_values(rec)
                    if len(row_vals) < int(1):
                        raise UserError(_("Please ensure that you selected the correct file"))
                    
                    if name != '' and row_vals[0] != '':
                        vals['attribute_line_ids'] = attribute_line_ids
                        _logger.warning(vals)
                        self.env['product.template'].create(vals)
                        attribute_line_ids = []

                    if row_vals[0] != '':
                        name = row_vals[0]
                        vals['name'] = name

                    if row_vals[1] != '':
                        vals['sale_ok'] = row_vals[1]

                    if row_vals[2] != '':
                        vals['purchase_ok'] = row_vals[2]

                    if row_vals[3] != '':
                        vals['detailed_type'] = PRODUCT_TYPE[row_vals[3]]
                    
                    if row_vals[4] != '':
                        categ_id = self.env['product.category'].search([ ('name', '=', row_vals[4]) ], limit=1)
                        if not categ_id:
                            raise UserError(f"{row_vals[4]} not Found")
                        vals['categ_id'] = categ_id.id

                    if row_vals[5] != '':
                        uom_id = self.env['uom.uom'].search([ ('name', '=', row_vals[5]) ], limit=1)
                        if not uom_id:
                            raise UserError(f"{row_vals[5]} not Found")
                        vals['uom_id'] = uom_id.id

                    if row_vals[7] != '' and row_vals[8] != '':
                        value_ids = []
                        attribute_id = self.env['product.attribute'].search([ ('name', '=', row_vals[7]) ], limit=1)
                        if not attribute_id:
                            raise UserError(f"{row_vals[7]} not Found")
                        variants = row_vals[8].split(',')
                        for variant in variants:
                            value = self.env['product.attribute.value'].search([ 
                                ('attribute_id', '=', attribute_id.id),
                                ('name', '=', variant),
                            ], limit=1)
                            if not value:
                                raise UserError(f"{variant} in {attribute_id.name} not Found")
                            value_ids.append(value.id)

                        attribute_line_ids.append((0,0,{
                            'attribute_id': attribute_id.id,
                            'value_ids': value_ids
                        }))

        except UserError as e:
            raise UserError(str(e))