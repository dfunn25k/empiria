import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class XLSXReportController(http.Controller):
    @http.route("/xlsx_report", type="http", auth="user", methods=["POST"], csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name):

        report_obj = request.env[model].sudo()
        options = json.loads(options)

        try:
            if output_format == "xlsx":
                response = request.make_response(
                    None,
                    headers=[
                        ("Content-Type", "application/vnd.ms-excel"),
                        (
                            "Content-Disposition",
                            content_disposition(report_name + ".xlsx"),
                        ),
                    ],
                )

                report_obj.get_xlsx_report(options, response)
                response.set_cookie("fileToken", "dummy token")
                return response
        except Exception as event:
            serialize = http.serialize_exception(event)
            error = {"code": 200, "message": "Odoo Server Error", "data": serialize}
            return request.make_response(html_escape(json.dumps(error)))
