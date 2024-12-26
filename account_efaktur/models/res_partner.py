from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_efaktur_exported = fields.Boolean('Is E-Faktur Exported')
    date_efaktur_exported = fields.Datetime('E-Faktur Exported Date')

    tin = fields.Char('Taxpayer Identification Number')
    block = fields.Char('Block')
    number = fields.Char('number')
    neighbourhood = fields.Char('Neighbourhood')
    hamlet = fields.Char('Hamlet')

    is_union = fields.Boolean('Kawasan Berserikat?')
    complete_address = fields.Char('Complete Address', compute='_compute_complete_address_', store=True)

    @api.depends("country_id", "state_id", "city", "city_id", "subdistrict_id", "ward_id", "street", "street2", "block", "number", "neighbourhood", "hamlet")
    def _compute_complete_address_(self):
        for record in self:
            address = record.street or ""
            address += " " + (record.street2 or "")

            if record.block:
                address += " Block: " + record.block + ", "
            if record.number:
                address += " Number: " + record.number + ", "
            if record.neighbourhood:
                address += " Neighbourhood: " + record.neighbourhood
            if record.hamlet:
                address += " Hamlet: " + record.hamlet

            record.complete_address = address.upper()