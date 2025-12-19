from odoo import models, api
from datetime import datetime



class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    @api.model
    def currency_rate_update(self, currency_id, new_rate):
        current_date = datetime.strftime(
            datetime.now(),
            '%Y-%m-%d'
        )
        rate_id = self.create({
            'name': current_date,
            'rate': new_rate,
            'company_id': self.env.user.company_id.id,
            'currency_id': currency_id
        })
        return rate_id.read()[0]

    @api.constrains('name', 'currency_id', 'company_id')
    def _constraint_currency_rate_unique_name_per_day(self):
        return
    @api.model
    def _verificate_contrainst(self):
        sql_verification = """
            SELECT
                indexname
            FROM
                pg_indexes
            WHERE
                tablename = 'res_currency_rate' AND  
                indexname = 'res_currency_rate_unique_name_per_day';
        """
        self.env.cr.execute(sql_verification)

        restriction = self.env.cr.fetchall()

        if len(restriction) > 0:
            sql_query = """ALTER TABLE res_currency_rate DROP CONSTRAINT IF EXISTS res_currency_rate_unique_name_per_day;"""
            self.env.cr.execute(sql_query)
