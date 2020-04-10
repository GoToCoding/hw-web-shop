import sys
from json import dumps

from flask import Flask, request

from .db import DB


API_V1_ROUTE = '/api/v1/'
def gen(url):
    return API_V1_ROUTE + url


class AppWrapper:
    def init_app(self):
        self.db = DB()

        self.app = Flask('auth')

        @self.app.route('/')
        def root_page():
            return 'auth: api version 1'

        self.add_routes()

        print('Successfully started auth service', file=sys.stderr)

    def close(self):
        self.db.close()

    # register; check; refresh

    def add_routes(self):
        @self.app.route(gen('register'), methods=['POST'])
        def register_user():
            params = request.get_json(force=True)
            if self.db.exists_email(params['email']):
                return dumps({
                    'result': 'failed',
                    'error': 'user with this email have already registred'
                })
            self.db.register_new(params['email'], params['password'])
            return dumps({'result': 'ok'})

        @self.app.route(gen('generate_tokens'), methods=['POST'])
        def generate_tokens():
            params = request.get_json(force=True)
            user_id = self.db.get_id_by_email_password(params['email'], params['password'])
            if user_id is None:
                return dumps({
                    'result': 'failed',
                    'error': 'given pair of (email, password) was not found'
                })
            result = self.db.generate_tokens(user_id)
            return dumps({'result': 'ok', **result})

        @self.app.route(gen('check_token'), methods=['POST'])
        def check_token():
            params = request.get_json(force=True)
            res = self.db.check_token(params['access_token'])
            if res is None:
                return dumps({'result': 'failed', 'error': 'bad token'})
            return dumps({'result': 'ok', 'user_id': res})

        @self.app.route(gen('refresh_token'), methods=['POST'])
        def refresh_token():
            params = request.get_json(force=True)
            result = self.db.refresh_token(params['access_token'], params['refresh_token'])
            if result is None:
                return dumps({'result': 'failed'})
            return dumps({'result': 'ok', **result})
