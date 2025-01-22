from odoo import _, api, fields, models


class DocumentsFolder(models.Model):
    _inherit = 'documents.folder'

    department_ids = fields.Many2many('hr.department', string='Write Departments', copy=True)
    read_department_ids = fields.Many2many('hr.department', 'documents_folder_read_departments', string='Read Departments', copy=True)