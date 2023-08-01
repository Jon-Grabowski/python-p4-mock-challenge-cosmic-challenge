#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api=Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
       scientists = [s.to_dict(rules = ('-missions',)) for s in Scientist.query.all()]
       response = make_response(scientists, 200)
       return response
    
    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )
        except Exception as e:
            return make_response({'errors': [str(e)]}, 422)
        
        db.session.add(new_scientist)
        db.session.commit()

        return make_response(new_scientist.to_dict(rules = ('-missions',)), 201)




api.add_resource(Scientists, '/scientists')

class Scientists_by_Id(Resource):
    def get (self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            response = {'error': 'Scientist not found'}
            return make_response(response, 404)
        response = make_response(scientist.to_dict(), 200)
        return response
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            response = {'error': 'Scientist not found'}
            return make_response(response, 404)
        data = request.get_json()
        try:
            for attr in data:
                setattr(scientist, attr, data[attr])
        except Exception as e:
            return make_response({'errors': [str(e)]}, 422)
        db.session.commit()
        return make_response(scientist.to_dict(rules = ('-missions',)), 200)
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            response = {'error': 'Scientist not found'}
            return make_response(response, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 200)

api.add_resource(Scientists_by_Id, '/scientists/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
