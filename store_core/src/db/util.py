import sys
from typing import Optional

import psycopg2

from ..models.product import Product

PRODUCTS_TABLE_NAME = 'products_table'

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
                CREATE TABLE IF NOT EXISTS {PRODUCTS_TABLE_NAME} (
                    product_id SERIAL PRIMARY KEY,
                    product_name varchar(45) NOT NULL,
                    product_category varchar(45) NOT NULL,
                    product_is_deleted boolean NOT NULL DEFAULT false
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
        id: int,
        with_deleted: bool = False
    ) -> dict:
        res = self.execute(f'''
            SELECT * FROM {PRODUCTS_TABLE_NAME}
            WHERE product_id = '{id}'
            LIMIT 1;
        ''', return_results=True)
        if res is None:
            return {}
        return Product(*res[0]).to_dict()

    def get_products(
        self,
        page: int = None,
        offset: int = None,
        count: int = None,
        with_deleted: bool = False
    ) -> dict:

        res = None

        deleted_query = '' if with_deleted else '\nWHERE product_is_deleted = false\n'
        pagination = ''

        if page is not None or (offset is not None and count is not None):
            if offset is None:
                offset = page * count
            pagination = f'\nLIMIT {count} OFFSET {offset}\n'

        res = self.execute(
            f'''SELECT * FROM {PRODUCTS_TABLE_NAME}''' +
                deleted_query +
                pagination + ';',
            return_results=True
        )

        products_count = self.execute(
            f'''SELECT count(*) FROM {PRODUCTS_TABLE_NAME}''' +
                deleted_query + ';',
            return_results=True
        )

        return {'products': [Product(*i).to_dict() for i in res], 'count': products_count[0][0]}

    def add_product(self, name: str, category: str) -> dict:
        self.execute(f'''
            INSERT INTO {PRODUCTS_TABLE_NAME}
            (product_name, product_category, product_is_deleted)
            VALUES ('{name}', '{category}', false);
        ''')

    def delete_product(self, id: int) -> None:
        self.execute(f'''
            UPDATE {PRODUCTS_TABLE_NAME}
            SET product_is_deleted = true
            WHERE product_id = '{id}';
        ''')

    def edit_product(self, product: Product) -> None:
        self.execute(f'''
            UPDATE {PRODUCTS_TABLE_NAME}
            SET product_is_deleted = false,
                product_name = '{product.name}',
                product_category = '{product.category}'
            WHERE product_id = '{product.id}';
        ''')

    def exist_product(self, id: int) -> bool:
        res = self.execute(f'''
            SELECT * FROM {PRODUCTS_TABLE_NAME}
            WHERE product_id = '{id}';
        ''', return_results=True)
        return res is not None
