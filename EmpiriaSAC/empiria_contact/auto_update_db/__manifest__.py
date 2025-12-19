{
    "name": "Auto Update DB",
    "summary": "Automatically update Odoo modules",
    "version": "16.0.2.0.1",
    "category": "Extra Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Ganemo, "
    "LasLabs,"
    "Juan José Scarafía, "
    "Tecnativa, "
    "ACSONE SA/NV, "
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    'autoinstall': True,
    "uninstall_hook": "uninstall_hook",
    "depends": ["base"],
    "data": ["views/ir_module_module.xml"],
    "development_status": "Production/Stable",
}
