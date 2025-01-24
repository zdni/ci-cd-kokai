from odoo import _, api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_partner_location(self, coords):
        current_user = self.env.user
        related_partner = current_user.partner_id

        related_partner.partner_latitude = coords.get('latitude')
        related_partner.partner_longitude = coords.get('longitude')
        return