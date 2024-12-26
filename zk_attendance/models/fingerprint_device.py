from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..controllers import main as c

class FingerprintDevice(models.Model):
    _name = 'fingerprint.device'
    _description = 'Fingerprint Device'

    name = fields.Char('Device Name')
    ip_address = fields.Char('IP Address')
    port = fields.Integer('Port', default=4370)
    sequence = fields.Integer('Sequence')
    device_password = fields.Char('Device Password', default=0)
    state = fields.Selection([
        ('0', 'Active'),
        ('1', 'Inactive')
    ], string='State', default='1')
    difference = fields.Float('Time Difference with UTC', default=0)

    def test_connection(self):
        try:
            with c.ConnectToDevice(self.ip_address, self.port, self.device_password) as conn:
                if conn:
                    self.write({ 'state': '0' })
        except:
            self.write({ 'state': '1' })
            raise UserError("Can't reach Fingerprint Device")

    def get_attendance(self):
        ctx = dict(default_device_id=self.id, active_ids=self.ids)
        return {
            'name': _('Employee Attendance'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.attendance.wizard',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }