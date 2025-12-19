from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        arch, view = super()._get_view(view_id, view_type, **options)

        if not self.env.user.has_group(
            "product_readonly_standard_price.group_edit_standard_price_product"
        ):
            for node in arch.xpath("//field[@name='standard_price']"):
                node.set("readonly", "1")

        return arch, view

    @api.model
    def _get_view_cache_key(self, view_id=None, view_type="form", **options):
        key = super()._get_view_cache_key(view_id, view_type, **options)
        return key + (
            self.env.user.has_group(
                "product_readonly_standard_price.group_edit_standard_price_product"
            ),
        )
