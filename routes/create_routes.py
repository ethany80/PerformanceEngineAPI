from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import controllers.data_controller as data_controller
from models.request_models import FromBlankRequest, FromAIRequest
import mem_data

create_routes = Blueprint("create", __name__, url_prefix="/api")


@create_routes.route("/from-blank", methods=["POST"])
@cross_origin()
def create_from_blank():
    request_data = request.get_json()

    from_blank_request = FromBlankRequest(
        report_name=request_data.get("name"),
        entities=request_data.get("entities"),
    )

    mem_data.create_type = "blank"

    mem_data.create_request = from_blank_request

    return jsonify({"layout": "layout-1"}), 201


@create_routes.route("/from-ai", methods=["POST"])
@cross_origin()
def create_from_ai():
    request_data = request.get_json()

    from_ai_request = FromAIRequest(
        prompt=request_data.get("prompt"),
        entities=request_data.get("entities"),
        begin=request_data.get("range1"),
        end=request_data.get("range2"),
    )

    mem_data.create_type = "ai"

    mem_data.create_request = from_ai_request

    return jsonify({"layout": "layout-1"}), 201
