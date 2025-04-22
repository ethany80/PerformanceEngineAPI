from flask import Blueprint, jsonify, request

test_routes = Blueprint("test", __name__, url_prefix="/api")


@test_routes.route("/test", methods=["GET"])
def test():
    return jsonify("hello world")
