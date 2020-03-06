import sys
from typing import Optional

import psycopg2

from ..models.product import Product

ITEMS_TABLE_NAME = 'products_table'

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

            self.execute(f'''
                CREATE TABLE IF NOT EXISTS {ITEMS_TABLE_NAME} (
                    product_id SERIAL PRIMARY KEY,
                    product_name varchar(45) NOT NULL,
                    product_code varchar(45) NOT NULL,
                    product_category varchar(45) NOT NULL,
                    product_is_deleted boolean NOT NULL
                );
            ''')

        except (Exception, psycopg2.Error) as error:
            print('Error while connecting to PostgreSQL', error, file=sys.stderr)
            raise error

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

    def get_product(
        self,
        name: str,
        with_deleted: bool = False
    ) -> dict:
        res = self.execute(f'''
            SELECT * FROM {ITEMS_TABLE_NAME}
            WHERE product_name = '{name}'
            LIMIT 1;
        ''', return_results=True)
        if res is None:
            return {}
        return Product(*res[0][1:]).to_dict()

    def get_products(
        self,
        page: int = None,
        offset: int = None,
        count: int = None,
        with_deleted: bool = False
    ) -> list:

        res = None

        deleted_query = '' if with_deleted else '\nWHERE product_is_deleted = false\n'
        pagination = ''

        if page is not None or (offset is not None and count is not None):
            if offset is None:
                offset = page * count
            pagination = f'\nLIMIT {count} OFFSET {offset}\n'

        res = self.execute(
            f'''SELECT * FROM {ITEMS_TABLE_NAME}''' +
                deleted_query +
                pagination + ';',
            return_results=True
        )

        return [Product(*(i[1:])).to_dict() for i in res]  # drop id column

    def add_product(self, product: Product) -> dict:
        self.execute(f'''
            INSERT INTO {ITEMS_TABLE_NAME}
            (product_name, product_code, product_category, product_is_deleted)
            VALUES ('{product.name}', '{product.code}', '{product.category}', false);
        ''')

    def delete_product(self, name: str) -> None:
        self.execute(f'''
            UPDATE {ITEMS_TABLE_NAME}
            SET product_is_deleted = true
            WHERE product_name = '{name}';
        ''')

    def edit_product(self, product: Product) -> None:
        self.execute(f'''
            UPDATE {ITEMS_TABLE_NAME}
            SET product_is_deleted = false,
                product_code = {product.code},
                product_category = {product.category}
            WHERE product_name = '{product.name}';
        ''')

    def exist_product(self, name: str) -> bool:
        res = self.execute(f'''
            SELECT * FROM {ITEMS_TABLE_NAME}
            WHERE product_name = '{name}';
        ''', return_results=True)
        print(res, name, file=sys.stderr)
        return res is not None

