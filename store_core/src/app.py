import requests
import sys
from json import dumps

from flask import Flask, request

from .db.util import DB
from .models.product import Product


API_V1_ROUTE = '/api/v1/'
def gen(url):
    return API_V1_ROUTE + url


class AppWrapper:
    def init_app(self):
        self.db = DB()

        self.app = Flask('web_shop')
        # self.app.config['APPLICATION_ROOT'] = API_V1_ROUTE

        @self.app.route('/')
        def root_page():
            return 'web_shop: api version 1'

        self.add_product_routes()

        print('Successfully started store_core', file=sys.stderr)

    def close(self):
        self.db.close()

    @staticmethod
    def is_authorized(headers):
        access_token = headers.get('Authorization', None)
        if access_token is None:
            return (False, 'Authorization header not given')
        res = requests.post(
            # 'http://0.0.0.0:5010/api/v1/check_token',
            'http://auth:5010/api/v1/check_token',
            json={'access_token': access_token}
        ).json()

        if res['result'] == 'ok':
            return (True, )
        return (False, res['error'])

    def add_product_routes(self):
        @self.app.route(gen('product'), methods=['POST'])
        def add_product():
            res = AppWrapper.is_authorized(request.headers)
            if not res[0]:
                return dumps({'failed': res[1]})
            params = request.get_json(force=True)  # if no application/json header force=True will ignore it
            self.db.add_product(params['name'], params['category'])
            return dumps({'result': 'ok'})

        @self.app.route(gen('products'), methods=['GET'])
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
                return dumps(self.db.get_products(page=int(page), count=int(count), with_deleted=with_deleted))
            return dumps(self.db.get_products(with_deleted=with_deleted))

        @self.app.route(gen('product/<product_id>'), methods=['GET'])
        def get_product(product_id):
            with_deleted = False
            if 'with_deleted' in request.args:
                with_deleted = request.args.get('with_deleted')
            return dumps(self.db.get_product(int(product_id), with_deleted))

        @self.app.route(gen('product'), methods=['DELETE'])
        def delete_product():
            res = AppWrapper.is_authorized(request.headers)
            if not res[0]:
                return dumps({'failed': res[1]})
            params = request.get_json(force=True)
            self.db.delete_product(params['id'])
            return dumps({'result': 'ok'})

        @self.app.route(gen('product'), methods=['PUT'])
        def edit_product():
            res = AppWrapper.is_authorized(request.headers)
            if not res[0]:
                return dumps({'failed': res[1]})
            params = request.get_json(force=True)
            if not self.db.exist_product(id=params['id']):
                return (dumps({'result': 'failed'}), 404)
            self.db.edit_product(Product(params['id'], params['name'], params['category']))
            return dumps({'result': 'ok'})
