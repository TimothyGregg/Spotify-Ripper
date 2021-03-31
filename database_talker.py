#!/usr/bin/env python

import mysql.connector

class db_talker:
    def __init__(self):
        self.db_connection = mysql.connector.connect(
            host = "localhost",
            user = "root",
            passwd = "Sooper Secret",
            database = "spotify"
        )
        self.mydb = self.db_connection.cursor()

    def modify(self, statement):
        self.execute(statement)
        self.commit()

    # Because SELECT doesn't need a COMMIT and in fact errors
    def execute(self, statement):
        # print(statement)
        self.mydb.execute(statement)

    def commit(self):
        self.db_connection.commit()

    def fetchone(self):
        return self.mydb.fetchone()

    def show_table(self, table_name):
        statement = 'SELECT * FROM ' + table_name + ';'
        self.mydb.execute(statement)
        results = self.mydb.fetchall()
        for x in results: print(x)






'''
db = db_talker()

statement = \
"""
DROP TABLE IF EXISTS access_data;
"""

db.execute(statement)

statement = \
"""
CREATE TABLE IF NOT EXISTS access_data(
    access_token	TEXT,
    refresh_token	TEXT,
    client_id		TEXT,
    client_secret	TEXT,
    redirect_uri	TEXT
    );
"""

db.execute(statement)

statement = \
"""
INSERT INTO access_data (access_token, refresh_token, client_id, client_secret, redirect_uri)
VALUES (
    'BQCCEgAUgzQMFrmhLgnPmKbDWfL4vwkowwXiMYd4w5fKO_EvLrz7ur8bpiiTjA3g4AzvUs6Ki4H8pImJoIwOG2B1SCGx-gZZKb31QGkSk9SbOKdaQ_6GLjKhTfmYEM52poWL0hkRIX0GnrH2qIThpueOStDzJFE',
    'AQBLa7WjHD95WI-0xYksyC-jr01-QFmn7hIIuL2VUzmgSR1RuYu8UR_jGz1ocERwOPcFpm1QLkgA4jM-OXfhSp9OI8LM6Kc7l6LGjJ0cT9vXjlB4jCTD8zluX7VfpiWI6NA',
    'd97f7a723b6348f4b32e057abeffc131',
    'f4a18aad07f04e80b8fda69709b38c86',
    'https://google.com'
);
"""

db.execute(statement)

db.show_table('access_data')
'''