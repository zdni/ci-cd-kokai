from odoo import _, api, fields, models, http
from odoo.exceptions import ValidationError

import base64
import requests
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_py3o(self):
        return self.env.ref("report_sale_order.action_report_sale_order_py3o").report_action(self, config=False)

    def _get_director(self):
        self.ensure_one()
        director = self.env.company.director_id.name
        return director

    def _get_string_priority(self):
        self.ensure_one()
        priority = dict(self._fields['priority'].selection).get(self.priority)
        return priority

    def _get_string_type(self):
        self.ensure_one()
        type = dict(self._fields['type'].selection).get(self.type)
        return type