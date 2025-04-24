class GraphRequest:
    def __init__(self, ids, data_type, range, data_points, chart_type):
        self.ids = ids
        self.data_type = data_type
        self.range = range
        self.data_points = data_points
        self.chart_type = chart_type

    def to_dict(self):
        return {
            "id": self.ids,
            "type": self.data_type,
            "range": self.range,
            "dataPoints": self.data_points,
            "chartType": self.chart_type,
        }


class GraphReturn:
    def __init__(self, title, chart_type, chart_model_data):
        self.title = title
        self.chart_type = chart_type
        self.chart_model_data = chart_model_data

    def to_dict(self):
        return {
            "title": self.title,
            "type": self.chart_type,
            "chart-data": self.chart_model_data.to_dict(),
        }


class FromBlankRequest:
    def __init__(self, report_name, entities):
        self.repot_name = report_name
        self.entities = entities


class FromAIRequest:
    def __init__(self, prompt, entities, begin, end):
        self.prompt = prompt
        self.entities = entities
        self.begin = begin
        self.end = end
