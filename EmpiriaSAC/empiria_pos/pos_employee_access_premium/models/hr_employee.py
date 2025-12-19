from odoo import fields, models


class HrEmployee(models.AbstractModel):
    _inherit = "hr.employee.base"

    pos_access_close = fields.Boolean(
        string="Access to close the POS",
        default=True,
        help="Enabling this will allow the user to close the POS"
    )
    pos_access_decrease_quantity = fields.Boolean(
        string="Access to decrease the quantity in the order lines",
        default=True,
        help="Enabling this will allow the user to decrease the quantity on the order lines"
    )
    pos_access_delete_order = fields.Boolean(
        string="Access to the removal of orders",
        default=True,
        help="Enabling this will allow the user to delete orders"
    )
    pos_access_delete_orderline = fields.Boolean(
        string="Access to delete order lines",
        default=True,
        help="Enabling this will allow the user to delete the order lines"
    )
    pos_access_discount = fields.Boolean(
        string="Access to discounts",
        default=True,
        help="Enabling this will allow the user to apply discount"
    )
    pos_access_payment = fields.Boolean(
        string="Access to payment",
        default=True,
        help="Enabling this will allow the user to apply the payment",
    )
    pos_access_price = fields.Boolean(
        string="Access to price change",
        default=True,
        help="Enabling this will allow the user to change the price"
    )
