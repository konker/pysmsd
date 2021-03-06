#
# pysmsd.handler.cultar_handler.py
#
# Copyright 2014 Helsinki Institute for Information Technology
# and the authors.
#
# Authors: Konrad Markus <konrad.markus@hiit.fi>
#

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import logging
import subprocess
from pysmsd.handlers import BaseSMSHandler

AUTHORIZED_NUMBERS = ('+358465727140', '+358405518195', '+358440670912')


class Handler(BaseSMSHandler):
    def __init__(self, db):
        self.system_client_id = db.get_system_client_id()


    def handle(self, db, id):
        if self.system_client_id is not None:
            message = db.get_in_message(id)
            if message['Keyword'].lower() == 'cultar':
                if message['Number'] in AUTHORIZED_NUMBERS:
                    print("Processing keyword %s for %s" % (message['Keyword'].lower(), message['Number']))
                    self.process_command(db, message)


    def process_command(self, db, message):
        tokens = message['Rest'].split(' ')
        if len(tokens) < 2:
            return

        try:
            if tokens[0].lower() == 'status':
                ret = subprocess.check_output(["/bin/systemctl", "status", "mloma-server-%s.service" % tokens[1].upper()])

            elif tokens[0].lower() == 'stop':
                ret = subprocess.check_output(["/bin/systemctl", "stop", "mloma-server-%s.service" % tokens[1].upper()])

            elif tokens[0].lower() == 'start':
                ret = subprocess.check_output(["/bin/systemctl", "start", "mloma-server-%s.service" % tokens[1].upper()])

            elif tokens[0].lower() == 'restart':
                ret = subprocess.check_output(["/bin/systemctl", "restart", "mloma-server-%s.service" % tokens[1].upper()])

            else:
                ret = "unknown command: %s" % tokens[1]

        except subprocess.CalledProcessError as ex:
            ret = "mloma-server-%s.service is DOWN" % tokens[1].upper()


        if self.system_client_id is not None:
            db.insert_out_message(dict(Number=message['Number'], Text=ret.decode('utf-8')),
                                  self.system_client_id)


