# -*- coding: utf-8 -*-

from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def post_install_hook(cr, registry):
    # Obtén el entorno del modelo 'ir.actions.server'
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Busca la acción del servidor y ejecútala
    action = env.ref("l10n_pe_account_reten.action_create_retention_journal")
    if action:
        action.sudo().run()
