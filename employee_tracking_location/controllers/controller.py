from odoo import http, tools, _, SUPERUSER_ID
from odoo.http import content_disposition, Controller, request, route


class TrackingLocationController(Controller):

    @route(['/api/tracking-location'], type='http', auth='public')
    def post_tracking_location(self, **kwargs):
        user_id = kwargs.get('user_id')
        date = kwargs.get('date')
        location_id = kwargs.get('location_id')
        area_id = kwargs.get('area_id')
        longitudinal = kwargs.get('longitudinal')
        latitude = kwargs.get('latitude')

        vals = {
            'user_id': user_id,
            'date': date,
            'location_id': location_id,
            'area_id': area_id,
            'longitudinal': longitudinal,
            'latitude': latitude,
        }