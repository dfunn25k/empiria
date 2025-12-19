from odoo import models, fields, api, _

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    
    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get('default_sunat_sequence_id'):
                result.append((record.id, record.prefix))
            else:
                result.append((record.id, record.name))
        return result
    
