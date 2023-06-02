from flask import Flask, jsonify, request, Blueprint
from flask_caching import Cache
from flasgger import Swagger, swag_from
import uuid

app = Flask(__name__)
swagger = Swagger(app)

# Cache Configuration
config = {"DEBUG": True, "CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}
app.config.from_mapping(config)
cache = Cache(app)

plants_bp = Blueprint("plants", __name__, url_prefix="/api/v1/plants")

# Plants Data
initial_plant = {
    "plantid": str(uuid.uuid4()),
    "nom": "nom",
    "planttype": "type",
    "etat": "etat",
    "datemaj": "24/2/2000",
    "description": "any description",
}
plants_list = [initial_plant]


@swag_from("./swagger.yaml")
@plants_bp.route("", methods=["POST"])
def create_plant():
    data = request.get_json()
    plant = {
        "plantid": str(uuid.uuid4()),
        "nom": data["nom"],
        "planttype": data["planttype"],
        "etat": data["etat"],
        "datemaj": data["datemaj"],
        "description": data["description"],
    }
    plants_list.append(plant)
    cache.set(plant["plantid"], plant)
    return jsonify({"message": f"Plant Created successfully {plant}"}), 201


@swag_from("./swagger.yaml")
@plants_bp.route("", methods=["GET"])
def get_all_plants():
    result = []
    for plant in plants_list:
        result.append(cache.get(plant["plantid"]))
    return jsonify(result), 200


@swag_from("./swagger.yaml")
@plants_bp.route("/<plantid>", methods=["GET"])
def get_plant_by_id(plantid):
    plant = cache.get(plantid)
    if plant:
        return jsonify(plant), 200
    else:
        return jsonify({"message": "Plant not found"}), 404


@swag_from("./swagger.yaml")
@plants_bp.route("/<plantid>", methods=["PUT"])
def update_plant_by_id(plantid):
    data = request.get_json()
    plant = cache.get(plantid)
    if plant:
        plant["nom"] = data["nom"]
        plant["planttype"] = data["planttype"]
        plant["etat"] = data["etat"]
        plant["datemaj"] = data["datemaj"]
        plant["description"] = data["description"]
        cache.set(plantid, plant)
        return jsonify({"message": f"Plant updated successfully {plant}"}), 200
    else:
        return jsonify({"message": "Plant not found"}), 404


@swag_from("./swagger.yaml")
@plants_bp.route("/<plantid>", methods=["DELETE"])
def delete_plant_by_id(plantid):
    for i, plant in enumerate(plants_list):
        if plant["plantid"] == plantid:
            plants_list.pop(i)
            cache.delete(plantid)
            return jsonify({"message": "Plant deleted successfully"}), 204
    else:
        return jsonify({"message": "Plant not found"}), 404


app.register_blueprint(plants_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)