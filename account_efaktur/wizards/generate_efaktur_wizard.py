from odoo import api, fields, models, _

class GenerateEfakturWizard(models.TransientModel):
    _name = 'generate.efaktur.wizard'
    
    start_serial = fields.Char('Start Serial')
    end_serial = fields.Char('End Serial')
    year = fields.Integer("Year")

    def confirm_button(self):
        self.ensure_one()
        start = self.start_serial
        end = self.end_serial
        
        #017-17-34018714
        a = start.split("-")
        b = end.split("-")
        
        for i in range(int(a[2]), int(b[2])+1):
            nomor = "%s-%s-%08d" % (a[0],a[1],i)
            self.env['account.efaktur'].create({
                'year': self.year,
                'name': nomor,
            })
        return
