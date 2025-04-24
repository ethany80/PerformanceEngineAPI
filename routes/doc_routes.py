from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import controllers.data_controller as data_controller
import controllers.openai_controller as openai_controller
from models.request_models import FromBlankRequest, FromAIRequest
import mem_data

doc_routes = Blueprint("doc", __name__, url_prefix="/api")


@doc_routes.route("/doc", methods=["GET"])
@cross_origin()
def get_doc():

    all_entities = data_controller.get_all_entities()

    filtered_entities = {
        key: value
        for key, value in all_entities.items()
        if key in mem_data.create_request.entities
    }

    data_types = None

    data_types = {
        "Market Value": {
            "types": ["line", "bar"],
            "range2-enabled": True,
            "can-be-multiple": True,
        },
        "Return": {
            "types": ["line", "bar"],
            "range2-enabled": True,
            "can-be-multiple": True,
        },
        "Asset Allocation": {
            "types": ["pie"],
            "range2-enabled": False,
            "can-be-multiple": False,
        },
    }

    print(filtered_entities)

    for key, entity in filtered_entities.items():
        if "Acc" in key:
            entity["types"] = ["Return", "Market Value", "Asset Allocation"]
        else:
            entity["types"] = ["Return", "Market Value"]

    if mem_data.create_type == "ai":
        return jsonify(
            {
                "entities": filtered_entities,
                "data-types": data_types,
                "visualizations": openai_controller.get_ai_charts(
                    mem_data.create_request.entities,
                    mem_data.create_request.prompt,
                    mem_data.create_request.begin,
                    mem_data.create_request.end,
                ),
            }
        )
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
