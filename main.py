from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_caching import Cache
import requests
import json

BASE = 'https://api.hatchways.io/assessment/blog/posts'

cache = Cache()

app = Flask(__name__)
api = Api(app)
cache.init_app(app)

app.config['CACHE_TYPE'] = 'simple'

#/api/posts RequestParser
posts_get_args = reqparse.RequestParser()
posts_get_args.add_argument('tags', type=str, help='Tags parameter is required', required=True)
posts_get_args.add_argument('sortBy', type=str, default='id', help='The field to sort the posts')
posts_get_args.add_argument('direction', type=str, default='asc', help='The direction for sorting')

class BlogPost(Resource):
    @app.route('/api/ping', methods=['GET'])
    def get_ping():
        response = requests.get(BASE, {'tag': ' '})
        if response.status_code == 200:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    
    @app.route('/api/posts', methods=['GET'])
    @cache.cached(timeout=60)
    def get_posts():
        sortBy_checking = ['id', 'reads', 'likes', 'popularity']
        args = posts_get_args.parse_args()
        tags = args['tags'].split(',')
        all_response = {'posts': []}
        
        #query for each tag
        for i in tags:
            response = requests.get(BASE, {'tag': i})
            if response.status_code != 200:
                return {'error': 'Tags parameter is required'}, 400
            result = json.loads(response.text)
            for i in result['posts']:
                all_response['posts'].extend(result['posts'])
        
        #de-duplication
        unique = {each['id']: each for each in all_response['posts']}.values()
        final_response = {'posts': []}
        final_response['posts'].extend(unique) 

        #sorting
        if args['sortBy'] not in sortBy_checking:
            return {'error': 'sortBy parameter is invalid'}, 400
        if args['direction'] == 'asc':
            final_response['posts'].sort(key=lambda x:x[args['sortBy']])
            return final_response, 200
        elif args['direction'] == 'desc':
            final_response['posts'].sort(key=lambda x:x[args['sortBy']], reverse=True)
            return final_response, 200
        else:
            return {'error': 'direction parameter is invalid'}, 400

if __name__ == '__main__':
    app.run(host='localhost', port=5000, threaded=True)