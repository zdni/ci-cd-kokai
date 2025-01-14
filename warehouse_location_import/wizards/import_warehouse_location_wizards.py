from odoo import _, api, fields, models
import base64, binascii, csv, io, tempfile, requests, xlrd
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class ImportWarehouseLocationWizard(models.TransientModel):
    _name = 'import.warehouse.location.wizard'
    _description = 'Import Warehouse Location Wizard'

    file = fields.Binary('File Excel')

    def action_import(self):
        LOCATION_TYPE = {
            'Vendor Location': 'supplier',
            'View': 'view',
            'Internal Location': 'internal',
            'Customer Location': 'customer',
            'Inventory Loss': 'inventory',
            'Production': 'production',
            'Transit Location': 'transit',
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

            for rec in range(sheet.nrows):
                if rec >= 1:
                    row_vals = sheet.row_values(rec)
                    if len(row_vals) < int(2):
                        raise UserError(_("Please ensure that you selected the correct file"))

                    company = self.env['res.company'].search([ ('name', '=', row_vals[4]) ], limit=1)
                    if not company:
                        raise UserError(f"Company f{row_vals[4]} not Found")

                    warehouse = self.env['stock.warehouse'].search([
                        ('name', '=', row_vals[2]),
                        ('company_id', '=', company.id),
                    ], limit=1)
                    if not warehouse:
                        raise UserError(f"Warehouse f{row_vals[2]} in {company.name} not Found")

                    parent_location = self.env['stock.location'].search([ 
                        ('complete_name', '=', row_vals[1]),
                        ('warehouse_id', '=', warehouse.id)
                    ], limit=1)
                    if not parent_location:
                        raise UserError(f"Parent {row_vals[1]} in {warehouse.name} not Found")

                    self.env['stock.location'].create({
                        'name': row_vals[0],
                        'location_id': parent_location.id,
                        'warehouse_id': warehouse.id,
                        'usage': LOCATION_TYPE[row_vals[3]],
                        'company_id': company.id,
                    })
        except UserError as e:
            raise UserError(str(e))
