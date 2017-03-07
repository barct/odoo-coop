from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
import base64


class Binary(http.Controller):
    @http.route('/web/binary/cesp', type='http', auth="public")
    @serialize_exception
    def download_document(self, period, **kw):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.registry['infocoop_tab_fact']
        cr, uid, context = request.cr, request.uid, request.context
        filecontent = "aveztruz"
        return request.make_response(
            filecontent,
            [('Content-Type', 'text/plain'),
             ('Content-Disposition',
             content_disposition("cesp.txt"))])
