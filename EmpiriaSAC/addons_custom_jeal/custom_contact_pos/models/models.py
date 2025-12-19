from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("vat", "l10n_latam_identification_type_id")
    def _check_unique_identification(self):
        for record in self:
            if record.vat and record.l10n_latam_identification_type_id:
                existing_partner = self.search(
                    [
                        ("id", "!=", record.id),
                        ("vat", "=", record.vat),
                        (
                            "l10n_latam_identification_type_id",
                            "=",
                            record.l10n_latam_identification_type_id.id,
                        ),
                    ]
                )
                if existing_partner:
                    raise ValidationError(
                        'El cliente con el número de identificación "{}" y tipo de documento "{}" ya existe.'.format(
                            record.vat,
                            record.l10n_latam_identification_type_id.display_name,
                        )
                    )
