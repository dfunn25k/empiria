odoo.define('pos_ticket_base_template.PosGlobalState', function (require) {
    "use strict";

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosTicketBaseTemplatePosGlobalState = PosGlobalState => class PosTicketBaseTemplatePosGlobalState extends PosGlobalState {
        get_report_action_name() {
            return 'account.account_invoices';
        }
        async report_action_backend(account_move) {
            await this.env.legacyActionManager.do_action(this.get_report_action_name(), {
                additional_context: {
                    active_ids: [account_move],
                },
            });
        }
    }
    Registries.Model.extend(PosGlobalState, PosTicketBaseTemplatePosGlobalState);
});
