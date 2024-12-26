from odoo import _, api, fields, models


class HelpdeskTag(models.Model):
    _name = 'helpdesk.tag'
    _description = 'Helpdesk Tag'

    name = fields.Char('Name')


class HelpdeskType(models.Model):
    _name = 'helpdesk.type'
    _description = 'Helpdesk Type'

    name = fields.Char('Name')


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Helpdesk Stage'
    _order = 'sequence ASC, id ASC'

    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Name')
    is_progress = fields.Boolean('Is Progress Stage?', default=False)
    is_close = fields.Boolean('Is Close Stage?', default=False)