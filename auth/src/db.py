import sys
from typing import Optional

import psycopg2
import secrets

USERS_TABLE_NAME = 'users_table'
TOKENS_TABLE_NAME = 'tokens_table'

ACCESS_TOKEN_TTL = 25  # just for test
REFRESH_TOKEN_TTL = 60

class DB:

    def __init__(self):
        self.initialize_table()

    def initialize_table(self):
        try:
            self.connection = psycopg2.connect(
                user = 'postgres',
                password = 'postgresql',
                host = 'db',
                port = '5432',
                database = 'postgres'
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()

            # self.execute(f'''
            #     DROP TABLE IF EXISTS {PRODUCTS_TABLE_NAME};
            # ''')

            self.execute(f'''
                CREATE TABLE IF NOT EXISTS {USERS_TABLE_NAME} (
                    user_id SERIAL PRIMARY KEY,
                    user_email varchar(100) NOT NULL,
                    user_password varchar(100) NOT NULL
                );
            ''')
            self.execute(f'''
                CREATE TABLE IF NOT EXISTS {TOKENS_TABLE_NAME} (
                    user_id integer UNIQUE,
                    access_token varchar(100) NOT NULL,
                    refresh_token varchar(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

        except (Exception, psycopg2.Error) as error:
            print('Error while connecting to PostgreSQL', error, file=sys.stderr)
            raise error

    @staticmethod
    def generate_access_refresh_token():
        access_token = secrets.token_hex(24)
        refresh_token = secrets.token_hex(24)
        return (access_token, refresh_token)

    def close(self) -> None:
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print('PostgreSQL connection is successfully closed', file=sys.stderr)

    def execute(self, query: str, return_results: bool = False) -> Optional[dict]:
        print(query, file=sys.stderr)
        self.cursor.execute(query)
        print('execute: success!', file=sys.stderr)
        if return_results:
            return self.cursor.fetchall()
        return None

    def exists_email(self, email: str) -> bool:
        res = self.execute(f'''
            SELECT * FROM {USERS_TABLE_NAME}
            WHERE user_email = '{email}';
        ''', return_results=True)
        print(res, file=sys.stderr)
        return bool(res)

    def get_id_by_email_password(self, email: str, password: str) -> Optional[int]:
        res = self.execute(f'''
            SELECT user_id FROM {USERS_TABLE_NAME}
            WHERE user_email = '{email}' and user_password = '{password}';
        ''', return_results=True)
        if res:
            return res[0][0]
        return None

    def register_new(self, email: str, password: str) -> None:
        self.execute(f'''
            INSERT INTO {USERS_TABLE_NAME}
            (user_email, user_password)
            VALUES ('{email}', '{password}');
        ''')

    def generate_tokens(self, user_id: str) -> dict:
        access_token, refresh_token = DB.generate_access_refresh_token()
        self.execute(f'''
            INSERT INTO {TOKENS_TABLE_NAME}
            (user_id, access_token, refresh_token)
            VALUES ('{user_id}', '{access_token}', '{refresh_token}')
            ON CONFLICT (user_id)
            DO
            UPDATE
                SET access_token = '{access_token}',
                    refresh_token = '{refresh_token}',
                    created_at = DEFAULT;
        ''')
        return {'access_token': access_token, 'refresh_token': refresh_token}

    def check_token(self, access_token: str) -> Optional[int]:
        res = self.execute(f'''
            SELECT user_id FROM {TOKENS_TABLE_NAME}
            WHERE created_at + {ACCESS_TOKEN_TTL} * interval '1 second' > CURRENT_TIMESTAMP and
                  access_token = '{access_token}';
        ''', return_results=True)
        print('HERE\n', res, file=sys.stderr)
        if res:
            return res[0][0]
        return None

    def refresh_token(self, access_token: str, refresh_token: str) -> Optional[dict]:
        res = self.execute(f'''
            SELECT * FROM {TOKENS_TABLE_NAME}
            WHERE created_at + {REFRESH_TOKEN_TTL} * interval '1 second' > CURRENT_TIMESTAMP and
                  refresh_token = '{refresh_token}' and
                  access_token = '{access_token}';
        ''', return_results=True)
        if not res:
            return None
        new_access_token, new_refresh_token = DB.generate_access_refresh_token()
        self.execute(f'''
            UPDATE {TOKENS_TABLE_NAME}
            SET
                access_token = '{new_access_token}',
                refresh_token = '{new_refresh_token}'
            WHERE
                access_token = '{access_token}' and
                refresh_token = '{refresh_token}';
        ''')
        return {'access_token': new_access_token, 'refresh_token': new_refresh_token}
