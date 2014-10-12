#
# pysmsd.db.db
#
# Copyright 2010 Helsinki Institute for Information Technology
# and the authors.
#
# Authors: Jani Turunen <jani.turunen@hiit.fi>
#          Konrad Markus <konrad.markus@hiit.fi>
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

from __future__ import with_statement

import logging
import sqlite3
import bcrypt
from pysmsd.lib.utils import Singleton


class Db:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.cursor = None


    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()


    def get_connection(self):
        self.connect()
        return self.connection


    def get_cursor(self):
        self.connect()
        return self.cursor


    def close(self):
        if self.cursor is not None:
            self.cursor.close()

        if self.connection is not None:
            self.connection.close()


    def is_authorized(self, name, password):
        self.connect()
        self.cursor.execute("SELECT * FROM `clients` WHERE `name`=?", (name,))
        row = self.cursor.fetchone()

        if row:
            if bcrypt.hashpw(password, row['password']) == row['password']:
                return row['id']
        return None


    def get_system_client(self):
        self.connect()
        self.cursor.execute("SELECT * FROM `clients` WHERE `name`='SYSTEM'")
        row = self.cursor.fetchone()

        if row:
            return row
        return None


    def get_system_client_id(self):
        row = self.get_system_client()
        if row is not None:
            return row['id']
        return None


    def mark_in_messages(self, client_id, id_list):
        self.connect()
        seq = [(client_id, i) for i in id_list]
        self.cursor.executemany("UPDATE `in_messages` SET `marked_by`=?, `marked`=datetime('now'), `updated`=datetime('now') WHERE id=?", seq)
        self.connection.commit()


    def mark_in_message(self, client_id, id):
        self.connect()
        self.cursor.execute("UPDATE `in_messages` SET `marked_by`=?, `marked`=datetime('now'), `updated`=datetime('now') WHERE id=?", (client_id, id))
        self.connection.commit()


    def insert_in_message(self, m):
        self.connect()
        self.cursor.execute("INSERT INTO `in_messages`(`Number`, `Text`, `Length`, `Coding`, `Datetime`, `Keyword`, `Rest`, `created`, `updated`) VALUES(?,?,?,?,?,?,?, datetime('now'), datetime('now'))", (m['Number'], m['Text'], m['Length'], m['Coding'], m['Received'], m['Keyword'], m['Rest']))
        self.connection.commit()
        return self.cursor.lastrowid


    def get_in_message(self, id):
        self.connect()
        self.cursor.execute("SELECT * FROM `in_messages` WHERE `id`=?", (id,))
        return self.cursor.fetchone()



    def get_in_messages(self, keyword=None, include_marked=False):
        self.connect()
        if keyword:
            if include_marked:
                self.cursor.execute("SELECT * FROM `in_messages` WHERE `keyword`=? ORDER BY `Datetime`", (keyword,))
            else:
                self.cursor.execute("SELECT * FROM `in_messages` WHERE `keyword`=? AND `marked` IS NULL ORDER BY `Datetime`", (keyword,))
        else:
            if include_marked:
                self.cursor.execute("SELECT * FROM `in_messages` ORDER BY `Datetime`")
            else:
                self.cursor.execute("SELECT * FROM `in_messages` WHERE `marked` IS NULL ORDER BY `Datetime`")

        return self.cursor


    def insert_out_message(self, m, client_id):
        self.connect()
        self.cursor.execute("INSERT INTO `out_messages`(`Number`, `Text`, `Length`, `queued_by`, `queued`, `created`, `updated`) VALUES(?,?,?,?, datetime('now'), datetime('now'), datetime('now'))", (m['Number'], m['Text'], len(m['Text']), client_id))
        self.connection.commit()
        return self.cursor.lastrowid


    def get_out_message(self, id):
        self.connect()
        self.cursor.execute("SELECT * FROM `out_messages` WHERE `id`=?", (id,))
        return self.cursor.fetchone()


    def get_out_messages(self):
        self.connect()
        self.cursor.execute("SELECT * FROM `out_messages` ORDER BY `created`, `Datetime`")
        return self.cursor


    def get_unsent_out_messages(self):
        self.connect()
        self.cursor.execute("SELECT * FROM `out_messages` WHERE `Datetime` IS NULL ORDER BY `queued`")
        return self.cursor


    def mark_out_message(self, id):
        self.connect()
        self.cursor.execute("UPDATE `out_messages` SET `Datetime`=datetime('now'), `updated`=datetime('now') WHERE id=?", (id,))
        self.connection.commit()


