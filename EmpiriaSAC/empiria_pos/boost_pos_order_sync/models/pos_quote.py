from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosQuote(models.Model):
    _name = 'pos.quote'
    _description = 'POS quotes'

    name = fields.Char(
        string='Name'
    )
    quote_id = fields.Char(
        string='Quote identifier',
        readonly=True
    )
    table_json = fields.Text(
        string='Table JSON'
    )
    pos_res_info = fields.Text(
        string='Pos info'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User session'
    )
    date_order = fields.Datetime(
        string='Quote Date',
        readonly=True,
        index=True
    )
    lines = fields.One2many(
        comodel_name='pos.quote.line',
        inverse_name='quote_id',
        string='Quote lines',
        readonly=True
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        readonly=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer'
    )
    session_id = fields.Many2one(
        comodel_name='pos.session',
        string='From POS Session',
        index=True,
        readonly=True
    )
    note = fields.Text(
        string='Internal Notes'
    )
    to_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='To POS session',
        index=True,
        readonly=True
    )
    amount_total = fields.Float(
        string='Total',
        digits=0,
        readonly=True
    )
    amount_tax = fields.Float(
        string='Taxes',
        digits=0,
        readonly=True
    )
    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done"), ("cancel", "Cancel")],
        default='draft'
    )
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal position'
    )
    quote_sent = fields.Boolean(
        string='Quote sent'
    )

    @api.model
    def search_quote(self, args):
        if args.get('quotation_id'):
            result = self.search(
                [('quote_id', '=', args.get('quotation_id'))]).id
            if result:
                return True

    def write(self, vals):
        for obj in vals:
            if 'quote_id' in obj:
                found_ids = self.env['pos.quote'].search(
                    [('quote_id', '=', obj['quote_id'])]).ids
                if len(found_ids) > 0:
                    raise UserError(
                        _("Please use some other Quote Id !!!\nThis id has already been used for some other quote"))
        return super(PosQuote, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('quote_id') == '' or not vals.get('quote_id'):
                vals['quote_id'] = self.env['ir.sequence'].next_by_code(
                    'pos.quote')
        result = super(PosQuote, self).create(vals_list)
        return result

    @api.model
    def print_quote(self):
        report_ids = self.env['ir.actions.report.xml'].search([
            ('model', '=', 'pos.quote'),
            ('report_name', '=', 'boost_pos_order_sync.quote_order_report')
        ]).ids
        return report_ids and report_ids[0] or False

    @api.model
    def search_all_record(self, kwargs):
        results = {}
        record_list = []
        quote_ids = self.search(
            [('state', '=', 'draft'), ('to_session_id', '=', kwargs['session_id'])]).ids
        quote_objs = self.browse(quote_ids)

        for quote_obj in quote_objs:
            result = {
                'status': True,
                'quote_obj_id': quote_obj.id,
                'quote_id': quote_obj.quote_id,
                'pricelist_id': quote_obj.pricelist_id.id,
                'note': quote_obj.note,
                'amount_total': quote_obj.amount_total,
                'amount_tax': quote_obj.amount_tax,
                'partner_id': [quote_obj.partner_id.id, quote_obj.partner_id.name],
                'to_session_id': quote_obj.to_session_id.id,
                'from_session_id': quote_obj.session_id.config_id.display_name,
                'message': 'Quote Id does not belong to this POS session .'
            }
            if quote_obj.table_json:
                result['table_json'] = quote_obj.table_json
            result['line'] = []
            for line in quote_obj.lines:
                orderline = line.get_order_line_dict_data()
                result['line'].append(orderline)
            record_list.append(result)
        results['quote_list'] = record_list
        return results

    @api.model
    def load_quote_history(self, kwargs):
        results = {}
        quote_list = []
        quote_objs = self.search([('session_id', '=', kwargs['session_id'])])
        for quote_obj in quote_objs:
            result = {'quote_id': quote_obj.quote_id}
            if quote_obj.partner_id.name:
                result['partner_id'] = quote_obj.partner_id.name
            else:
                result['partner_id'] = '-'
            result['amount_total'] = quote_obj.amount_total
            result['to_session_id'] = quote_obj.to_session_id.config_id.display_name
            result["state"] = quote_obj.state[0].upper() + quote_obj.state[1:]
            quote_list.append(result)
        results['quote_list'] = quote_list
        return results

    def click_cancel(self):
        self.write({'state': 'cancel'})

    @api.depends('quote_id')
    def name_get(self):
        res = []
        for record in self:
            name = str(record.quote_id)
            res.append((record.id, name))
        return res
