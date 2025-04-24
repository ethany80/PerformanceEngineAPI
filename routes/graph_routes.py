from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import controllers.data_controller as data_controller
from models.request_models import GraphRequest, GraphReturn
from models.chart_models import Bar, Line, Pie

graph_routes = Blueprint("graph", __name__, url_prefix="/api")


@graph_routes.route("/graph", methods=["POST"])
@cross_origin()
def graph():
    request_data = request.get_json()

    graph_request = GraphRequest(
        ids=request_data.get("id"),
        data_type=request_data.get("type"),
        range=request_data.get("range"),
        data_points=request_data.get("dataPoints"),
        chart_type=request_data.get("chartType"),
    )

    entity_type = graph_request.ids[0][:3]

    if entity_type != "Acc" and entity_type != "Pos":
        return jsonify(error="id field must contain Pos or Acc"), 400

    ids = [id[3:] for id in graph_request.ids]

    if graph_request.chart_type == "table":
        return jsonify(
            GraphReturn(
                title="Overall Performance",
                chart_type="table",
                chart_model_data=data_controller.get_table_values(
                    ids,
                    graph_request.range[0],
                    graph_request.range[1],
                    entity_type,
                ),
            ).to_dict()
        )

    chart_data_set = None

    if graph_request.data_type == "Market Value":
        chart_data_set = data_controller.get_multidate_market_value(
            ids,
            graph_request.range[0],
            graph_request.range[1],
            graph_request.data_points,
            entity_type,
        )
    elif graph_request.data_type == "Return":
        chart_data_set = data_controller.get_multidate_twr(
            ids,
            graph_request.range[0],
            graph_request.range[1],
            graph_request.data_points,
            entity_type,
        )
    elif graph_request.data_type == "Asset Allocation":
        chart_data_set = data_controller.get_asset_allocation(
            ids,
            graph_request.range[0],
            entity_type,
        )
    else:
        return (
            jsonify(
                error="type field must be Market Value, Return, or Asset Allocation"
            ),
            400,
        )

    if graph_request.data_type in ["Market Value", "Return"]:
        if graph_request.chart_type == "bar-unused":
            return jsonify(
                GraphReturn(
                    title=f"{chart_data_set.chart_data_list[0].name} {graph_request.data_type}",
                    chart_type="bar-unused",
                    chart_model_data=Bar(
                        chart_data_set.dates,
                        chart_data_set.chart_data_list[0].values,
                    ),
                ).to_dict()
            )
        elif graph_request.chart_type == "bar":
            return jsonify(
                GraphReturn(
                    title=graph_request.data_type,
                    chart_type="bar",
                    chart_model_data=Bar(
                        chart_data_set.dates,
                        {
                            data.name: data.values
                            for data in chart_data_set.chart_data_list
                        },
                    ),
                ).to_dict()
            )
        elif graph_request.chart_type == "line-unused":
            return jsonify(
                GraphReturn(
                    title=f"{chart_data_set.chart_data_list[0].name} {graph_request.data_type}",
                    chart_type="line-unused",
                    chart_model_data=Line(
                        [
                            {"x": x, "y": y}
                            for x, y in zip(
                                list(range(1, len(chart_data_set.dates) + 1)),
                                chart_data_set.chart_data_list[0].values,
                            )
                        ],
                    ),
                ).to_dict()
            )
        elif graph_request.chart_type == "line":
            return jsonify(
                GraphReturn(
                    title=graph_request.data_type,
                    chart_type="line",
                    chart_model_data=Line(
                        {
                            data.name: [
                                {"x": x, "y": y}
                                for x, y in zip(
                                    list(range(1, len(chart_data_set.dates) + 1)),
                                    data.values,
                                )
                            ]
                            for data in chart_data_set.chart_data_list
                        },
                    ),
                ).to_dict()
            )
        else:
            return (
                jsonify(
                    error="chartType field types bar, multibar, line, or multiline can only display data types Market Value or Return"
                ),
                400,
            )

    if graph_request.data_type == "Asset Allocation":
        if graph_request.chart_type == "pie":
            return jsonify(
                GraphReturn(
                    title=graph_request.data_type,
                    chart_type="pie",
                    chart_model_data=Pie(
                        [
                            {"name": data.name, "value": data.values[0]}
                            for data in chart_data_set.chart_data_list
                        ],
                    ),
                ).to_dict()
            )
        else:
            return (
                jsonify(
                    error="chartType field type pie can only display data type AssetAllocation"
                ),
                400,
            )
