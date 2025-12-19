from odoo.addons.account.models.account_move_line import AccountMoveLine

def _search_panel_domain_image(self, field_name, domain, set_count=False, limit=False):
    return super(AccountMoveLine, self)._search_panel_domain_image(field_name, domain, set_count, limit)


AccountMoveLine._search_panel_domain_image = _search_panel_domain_image
