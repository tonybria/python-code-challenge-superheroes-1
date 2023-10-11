#!/usr/bin/env python3
from flask import Flask
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Hero, Power, hero_power

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return '<h1>Welcome home</h1>'

class Index (Resource):
    def get(self):
        response_dict={
            'Status':'success'
        }
        response = make_response(
            jsonify(response_dict
                    ),
                    200,
            
        )
        return response
api.add_resource(Index,'/')

#GET(heroes)

class Heroes(Resource):
    def get(self):
        heroes = []
        for hero in Hero.query.all():
            hero_data = {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name,
                "created_at": hero.created_at
            }
            heroes.append(hero_data)
        return make_response(jsonify(heroes), 200)
api.add_resource(Heroes, '/heroes')

#GET (/heroes/:id)

class HeroesById(Resource):
    def get(self,id):
        hero = Hero.query.filter_by(id=id).first()
        if hero:
             hero_data = {
                    "id": hero.id,
                    "name": hero.name,
                    "super_name": hero.super_name,
                    "powers": [
                        {
                            "id": power.id,
                            "name": power.name,
                            "description": power.description
                        }
                        for power in hero.powers
                    ]
                }
             return make_response(jsonify(hero_data), 200)
        else:
            response_dict = {
                "error": "Hero not found"
            }
            response = make_response(jsonify(response_dict), 404)
            return response
          
api.add_resource(HeroesById, '/heroes:<int:id>')

#GET(/Powers)

class Powers(Resource):
    def get(self):
        powers = []
        for power in Power.query.all():
            power_data={
                "id": power.id,
                "name": power.name,
                "description": power.description,
                "created_at":power.created_at,
                "hero_ps": [
                    {
                        "strength": hero_p.strength,
                        "hero_id": hero_p.hero_id
                    }
                    for hero_p in power.hero_ps
                ]

            }
            powers.append(power_data)
        return make_response(jsonify(powers),200)
    
api.add_resource(Powers, '/powers') 

 # GET (/powers/:id)
  
class PowersById(Resource):
    def get(self, id):
        powers = []
        power = Power.query.filter_by(id=id).first()
        if power:
            power_data = {
                "id": power.id,
                "name": power.name,
                "description": power.description,
                "created_at": power.created_at,
                "hero_ps": [
                    {
                        "strength": hero_p.strength,
                        "hero_id": hero_p.hero_id
                    }
                    for hero_p in power.hero_ps
                ]
            }
            powers.append(power_data)
            return make_response(jsonify(powers), 200)
        else:
               response_dict={
                "error": "Power not found"
               }
               response = make_response(
                jsonify(response_dict), 404
               )
               return response
           
    
  # PATCH /powers/:id
    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
         

        if power:
            description = request.form.get('description')

            if not description or len(description) < 20:
                response_dict = {
                   "errors": ["validation errors"]
                }
                response = make_response(jsonify(response_dict), 400)
                return response
            for attr in request.form:
                setattr(power, attr, request.form.get(attr))
            db.session.add(power)
            db.session.commit()
   
            power_data = {
                "id": power.id,
                "name": power.name,
                "description": power.description,
                "created_at": power.created_at
            
            }

            response = make_response(jsonify(power_data), 200)
            return response
        elif not power:
            response_dict = {
                "error": "Power not found"
            }
            response = make_response(jsonify(response_dict), 404)
            return response
        
       
api.add_resource(PowersById, '/powers/<int:id>')

# POST (/hero_powers)

class Hero_powers(Resource):
    def post(self):
        valid_strengths = ["Strong", "Weak", "Average"]
        
        data = request.get_json()
        strength = data.get('strength')
        power_id = data.get('power_id')
        hero_id = data.get('hero_id')
        
        if strength not in valid_strengths:
            response_dict = {
                "errors": ["validation errors"]
            }
            return make_response(jsonify(response_dict), 400)
        
        if strength and power_id and hero_id:
            hero = Hero.query.get(hero_id)
            power = Power.query.get(power_id)

            if hero and power:
                hero_power_entry = hero_power.insert().values(
                    strength=strength,
                    power_id=power_id,
                    hero_id=hero_id
                )

                db.session.execute(hero_power_entry)
                db.session.commit()

                hero_data = {
                    "id": hero.id,
                    "name": hero.name,
                    "super_name": hero.super_name,
                    "powers": [
                        {
                            "id": power.id,
                            "name": power.name,
                            "description": power.description
                        }
                        for power in hero.powers
                    ]
                }
                response = make_response(jsonify(hero_data), 201)
                return response
            else:
                response_dict = {
                    "error": "Invalid hero_id or power_id"
                }
                response = make_response(jsonify(response_dict), 404)
                return response
        else:
            response_dict = {
                "error": "Missing required fields"
            }
            response = make_response(jsonify(response_dict), 400)
            return response
              
api.add_resource(Hero_powers, '/hero_powers')

          
if __name__ == '__main__':
    app.run(port=5555)