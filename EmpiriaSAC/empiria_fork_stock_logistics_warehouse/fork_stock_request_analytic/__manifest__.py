{
    "name": "Fork Stock Request Analytic",
    "summary": "This module allows for users to be able to display and assign analytic accounts to stock requests.",
    "version": "16.0.0.0.1",
    "license": "Other proprietary",
    "website": "https://www.ganemo.co",
    "author": "Ganemo",
    "category": "Accounting",
    "depends": [
        "stock_request",
        "stock_analytic",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_request_views.xml",
        "views/stock_request_order_views.xml",
        "views/analytic_views.xml",
    ],
    "installable": True,
}
