from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AssignDrawingWizard(models.TransientModel):
    _name = 'assign.drawing.wizard'

    

    def button_process(self):
        self.ensure_one()
        
        if self.ref_id and self.stage_id:
            lead = self.ref_id

            history = {
                'lead_id': lead.id,
                'old_stage_id': lead.stage_id.id,
                'stage_id': self.stage_id.id,
                'user_id': self.env.user.id,
                'reason': self.reason,
                'date': fields.Datetime.now(),
            }
            lead.write({ 
                'stage_id': self.stage_id.id,
                'history_ids': [(0, 0, history)],
                'state': 'new',
            })
        else:
            raise ValidationError("Change Stage can't be Processed!")