from odoo import _, api, fields, models, tools
from lxml import etree
import json


class ProductUoM(models.Model):
    _inherit = "uom.uom"

    l10n_pe_edi_measure_unit_code = fields.Char(
        string="Measure unit code",
        help="Unit code that relates to a product in order to identify what measure unit it uses, the possible values"
        " that you can use here can be found in this URL",
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(ProductUoM, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        # if l10n_pe_edi is installed should not duplicate l10n_pe_edi_measure_unit_code in view
        if view_type == "form" and self.env.ref(
            "l10n_pe_edi.uom_uom_form_inherit_l10n_pe_edi"
        ):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//field[@name='l10n_pe_edi_measure_unit_code']"):
                modifiers = {"invisible": 1}
                node.set("modifiers", json.dumps(modifiers))
                break
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
