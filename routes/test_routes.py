from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

test_routes = Blueprint("test", __name__, url_prefix="/api")


@test_routes.route("/test", methods=["GET"])
@cross_origin()
def test():
    return jsonify("hello world")
