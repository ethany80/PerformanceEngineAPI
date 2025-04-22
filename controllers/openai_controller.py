from openai import OpenAI
import json
from models.request_models import GraphRequest
from models.chart_models import Visualization

client = OpenAI()


def get_ai_charts(entities, prompt, begin, end):
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": """
                based on the user prompt below, create a layout of a financial portfolio performance report.
                
                The available options for data type are Market Value, Return, and Asset Allocation. The available chart  types are Bar graph, Line graph, Pie chart, and Table. Market Value and Return can only be displayed in  a Bar graph or Line graph. Asset Allocation can only be displayed in a Pie chart. The Table chart type does  not need to specify a data type - for the data type field in a Table object, please just insert "null". Additionally, any list of charts can contain at most one Table, and it must be the last chart in the list if the list does contain a Table. There  must be 5 charts in the list of charts - no more, no less. For the "chart_type" field, the options (strict to the  casing and spelling) are "bar", "line", "pie", and "table". For the "data_type" field, the options, with  the same strict formatting, are "Market Value", "Asset Allocation", and "Return". You must only respond with  Json data of the chart list. The following is the json format that you should respond with: 
                                
                    {
                    "chart1": {
                            "chart_type": "chart_type_name",
                            "data_type": "data_type_name"
                    },
                    "chart2": {
                            "chart_type": "chart_type_name",
                            "data_type": "data_type_name"
                    }, ...
                    }
                                
                When you send the response, send it in the JSON format but as a raw string. Do not use any additional formatting or newlines. Only characters and spaces.
                """
                + f"\nUser Prompt: {prompt}",
            }
        ],
    )

    charts = json.loads(completion.choices[0].message.content)

    print(charts)

    chart_requests = []

    for _, chart_info in charts.items():
        chart_type = chart_info["chart_type"]
        data_type = chart_info["data_type"]

        if chart_type in ("bar", "line"):
            chart_type = f"multi{chart_type}" if len(entities) > 1 else chart_type

        chart_requests.append(
            GraphRequest(
                ids=entities,
                data_type=data_type,
                range=[begin, end],
                data_points=4,
                chart_type=chart_type,
            )
        )

    visualizations = []

    i = 0

    y = 1000

    while i < len(chart_requests) - 1:
        visualizations.append(
            Visualization(
                width=350,
                height=250,
                x=50,
                y=y - (i * 150),
                request=chart_requests[i].to_dict(),
            ).to_dict()
        )

        visualizations.append(
            Visualization(
                width=350,
                height=250,
                x=400,
                y=y - (i * 150),
                request=chart_requests[i + 1].to_dict(),
            ).to_dict()
        )

        i += 2

    if chart_requests[len(chart_requests) - 1].chart_type == "table":
        visualizations.append(
            Visualization(
                width=1000,
                height=350,
                x=50,
                y=400,
                request=chart_requests[len(chart_requests) - 1].to_dict(),
            ).to_dict()
        )
    else:
        visualizations.append(
            Visualization(
                width=350,
                height=250,
                x=250,
                y=400,
                request=chart_requests[len(chart_requests) - 1].to_dict(),
            ).to_dict()
        )

    return visualizations
