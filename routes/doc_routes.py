from flask import Blueprint, jsonify, request
import controllers.data_controller as data_controller
from models.request_models import FromBlankRequest, FromAIRequest
import mem_data

doc_routes = Blueprint("doc", __name__, url_prefix="/api")


@doc_routes.route("/doc", methods=["GET"])
def get_doc():

    data_types = {
        "Market Value": {
            "types": ["line", "multi-line", "bar", "table"],
            "range2-enabled": True,
            "can-be-multiple": True,
        },
        "Return": {
            "types": ["line", "multi-line", "bar", "table"],
            "range2-enabled": True,
            "can-be-multiple": True,
        },
        "Allocation": {
            "types": ["pie", "table"],
            "range2-enabled": False,
            "can-be-multiple": False,
        },
    }

    all_entities = data_controller.get_all_entities()

    filtered_entities = {
        key: value
        for key, value in all_entities.items()
        if key in mem_data.create_request.entities
    }

    if mem_data.create_type == "ai":
        return "test"
    elif mem_data.create_type == "blank":
        return jsonify(
            {
                "entities": filtered_entities,
                "data-types": data_types,
                "visualizations": {},
            }
        )
    else:
        return jsonify(error="create_type not set to ai or blank"), 500
