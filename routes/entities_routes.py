from flask import Blueprint, jsonify
import controllers.data_controller as data_controller


entities_routes = Blueprint("all-entities", __name__, url_prefix="/api")


@entities_routes.route("/all-entities", methods=["GET"])
def all_entities():
    return jsonify(data_controller.get_all_entities())
