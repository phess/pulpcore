# -*- coding: utf-8 -*-
#
# Copyright © 2010-2011 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

import web

from pulp.server.auditing import events
from pulp.server.auth.authorization import READ
from pulp.server.webservices import mongo
from pulp.server.webservices.controllers.base import JSONController

# audit events controller -----------------------------------------------------

class Events(JSONController):

    @JSONController.error_handler
    @JSONController.auth_required(READ)
    def GET(self):
        """
        [[wiki]]
        title: List Audited Events
        description: List all available audited events.
        method: GET
        path: /events/
        permission: READ
        success response: 200 OK
        failure response: None
        return: list of event objects
        object fields:
         * timestamp (int) - time the event occurred
         * principal_type (str) - type of the principal
         * principal (str) - principal that triggered the event
         * action (str) - name of the audited action
         * method (str) - name of the method called
         * params (list of str) - parameter passed to the method
         * result (str) - result of the method call or null if not recorded
         * exception (str) - name of the error that occurred, if any
         * traceback (str) - code traceback for the error, if any
        filters:
         * api (str) - the api name
         * method (str) - the method name
         * principal (str) - the caller of an api method
         * field (str) - which fields are returned for each event
         * limit (int) - limit the number of events returned
         * show=errors_only - only show events that have a traceback associated with them
        """
        valid_filters = ('principal', 'api', 'method', 'field', 'limit', 'show')
        filters = self.filters(valid_filters)

        show = filters.pop('show', [])
        errors_only = 'errors_only' in show

        limit = filters.pop('limit', None)
        if limit is not None:
            try:
                limit = int(limit[-1]) # last limit takes precedence
            except ValueError:
                return self.bad_request('Invalid value for limit parameter')

        fields = filters.pop('field', None)
        spec = mongo.filters_to_re_spec(filters)
        return self.ok(events(spec, fields, limit, errors_only))

# web.py application ----------------------------------------------------------

URLS = (
    '/$', Events,
)

application = web.application(URLS, globals())
