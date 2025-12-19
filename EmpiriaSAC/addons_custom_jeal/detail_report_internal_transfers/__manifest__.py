# -*- coding: utf-8 -*-
{
    "name": "Informe Detalle de Transferencias Internas",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com
    """,
    "description": """
        Long description of module's purpose
    """,
    "author": "JEAL",
    "website": "https://www.jeal.com",
    "category": "",
    "version": "16.0.0.0.1",
    "depends": ["base", "stock", "base_report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "data/paperformat_data.xml",
        "report/report_informe_bank.xml",
        "report/report_action.xml",
        "wizard/report_internal_transfers_view.xml",
        "views/menuitems.xml",
    ],
}
