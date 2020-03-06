import sys
from json import dumps

from flask import Flask, request

from .db.util import DB
from .models.product import Product


class AppWrapper:
    def init_app(self):
        self.db = DB()

        self.app = Flask('web_shop')

        @self.app.route('/')
        def root_page():
            return 'This is just root page!'

        self.add_product_routes()

    def close(self):
        self.db.close()

    def add_product_routes(self):
        @self.app.route('/add_product', methods=['POST'])
        def add_product():
            params = request.get_json(force=True)  # if no application/json header force=True will ignore it
            self.db.add_product(Product(params['name'], params['code'], params['category']))
            return ''

        @self.app.route('/products', methods=['GET'])
        def get_products():
            with_deleted = False
            if 'with_deleted' in request.args:
                with_deleted = request.args.get('with_deleted')
            if 'page' in request.args:
                page = request.args.get('page')
                count = 10
                if 'offset' in request.args:
                    return dumps({'status': 'failed', 'info': 'if `page` param is set, then only `count` param can be given'})
                if 'count' in request.args:
                    count = request.args.get('count')
                return dumps(self.db.get_products(page=page, count=count, with_deleted=with_deleted))
            return dumps(self.db.get_products(with_deleted=with_deleted))

        @self.app.route('/product_info/<product_name>', methods=['GET'])
        def get_product(product_name):
            with_deleted = False
            if 'with_deleted' in request.args:
                with_deleted = request.args.get('with_deleted')
            return dumps(self.db.get_product(product_name, with_deleted))

        @self.app.route('/remove_product', methods=['DELETE'])
        def delete_product():
            params = request.get_json(force=True)
            self.db.delete_product(params['name'])
            return ''

        @self.app.route('/edit_product', methods=['PUT'])
        def edit_product():
            params = request.get_json(force=True)
            if not self.db.exist_product(name=params['name']):
                return ('', 404)
            self.db.edit_product(Product(params['name'], params['code'], params['category']))
            return ''
