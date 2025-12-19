from odoo import api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create_from_ui(self, partner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        if partner.get('image_1920'):
            partner['image_1920'] = partner['image_1920'].split(',')[1]

        partner_id = partner.pop('id', False)
        if partner.get('l10n_latam_identification_type_id'):
            partner['l10n_latam_identification_type_id'] = int(partner['l10n_latam_identification_type_id'])
        if partner_id:
            self.browse(partner_id).write(partner)
            error_dialog = self.browse(partner_id).error_dialog
            if self.browse(partner_id).error_dialog:
                raise ValidationError(_('You must resolve the following observations before saving: \n %s' %
                                      error_dialog))
        else:
            partner['lang'] = self.env.user.lang
            partner_id = self.create(partner)
            if partner_id.error_dialog:
                raise ValidationError(_('You must resolve the following observations before saving: \n %s' %
                                      partner_id.error_dialog))
            partner_id = partner_id.id
        return partner_id
