from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    journal_assign_to_ids = fields.Many2many(
        comodel_name='res.users',
        string='Diario - Asignado a',
        compute='_compute_journal_assign_to_ids',
        store=True
    )

    @api.depends('journal_id', 'journal_id.assign_to_ids')
    def _compute_journal_assign_to_ids(self):
        """
        Compute the related users who have access to the journal of the account move.

        This method is a computed field that retrieves the related users from the journal's
        'assign_to_ids' field. It uses the 'env.cr.execute' method to perform a SQL query
        to fetch the journal_id of the current account move record. Then, it fetches the
        corresponding journal record and retrieves the 'assign_to_ids' field.
        This is to avoid the error maximum recursion depth exceeded in comparison when trying to get the journal_id from account.move (a computed field).

        Parameters:
        self (account.move): The current record of the account move model.

        Returns:
        None: The method updates the 'journal_assign_to_ids' field of the current record.
        """
        for record in self:
            self.env.cr.execute("SELECT journal_id FROM account_move where id = %(move_id)s", {
                'move_id': record.id,
            })
            query_journal_id = self.env.cr.fetchall()
            assign_to_ids = False
            if query_journal_id:
                journal_id = self.env['account.journal'].browse(query_journal_id[0][0])
                assign_to_ids = journal_id.assign_to_ids
            record.journal_assign_to_ids = assign_to_ids


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def _get_batch_available_journals(self, batch_result):
        """
            This function is used to get the available journals for the batch.
            It is used to restrict the journals that are accessible to the user.
        """
        res = super()._get_batch_available_journals(batch_result)
        user = self.env.user
        if not user.has_group("add_user_by_journal.res_groups_admin_journal_access"):
            new_res = self.env['account.journal']
            for journal in res:
                if journal.assign_to_ids and user.id in journal.assign_to_ids.ids:
                    new_res += journal
            res = new_res
        return res
