import os
import base64, binascii, csv, io, tempfile, requests, xlrd
from odoo import fields, models, _
from odoo.exceptions import UserError
import logging


_logger = logging.getLogger(__name__)


class HRContractImport(models.TransientModel):
    _name = 'hr.contract.import'
    _description = 'Import Contract of Employee'

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
            
            error = ''
            name = ''
            allowance_ids = []
            employee = False
            
            vals = {}
            for rec in range(sheet.nrows):
                if rec >= 1:
                    row_vals = sheet.row_values(rec)
                    if len(row_vals) < int(1):
                        raise UserError(_("Please ensure that you selected the correct file"))
                    

                    if name != '' and row_vals[0] != '' and employee:
                        vals['allowance_ids'] = allowance_ids
                        vals['wage'] = 1
                        _logger.warning(vals)
                        self.env['hr.contract'].create(vals)
                        allowance_ids = []

                    if row_vals[0] != '':
                        name = row_vals[0]
                        employee = self.env['hr.employee'].search([ ('name', '=', name) ], limit=1)
                        if not employee:
                            raise UserError(f"Employee {name} not Found || ")
                            error += f"Employee {name} not Found || "
                        vals['employee_id'] = employee.id
                        vals['department_id'] = employee.department_id.id
                        vals['job_id'] = employee.job_id.id
                        vals['hr_responsible_id'] = 2

                    if row_vals[2] != '':
                        aer_category = self.env['aer.category'].search([ ('name', '=', row_vals[2]) ], limit=1)
                        if not aer_category:
                            raise UserError(f"AER Category {row_vals[2]} not Found || ")
                            error += f"AER Category {row_vals[2]} not Found || "
                        if employee:
                            employee.write({ 'aer_category_id': aer_category.id })
                    
                    if row_vals[4] != '':
                        vals['name'] = row_vals[4]

                    if row_vals[5] != '':
                        vals['date_start'] = row_vals[5]

                    if row_vals[6] != '':
                        vals['date_end'] = row_vals[6]

                    if row_vals[12] != '' and row_vals[13] != '':
                        allowance = self.env['hr.allowance.type'].search([ ('name', '=', row_vals[12]) ], limit=1)
                        if not allowance:
                            raise UserError(f"{row_vals[12]} not Found")
                        allowance_ids.append((0,0, {
                            'allowance_id': allowance.id,
                            'value': row_vals[13],
                        }))

        except UserError as e:
            raise UserError(str(e))