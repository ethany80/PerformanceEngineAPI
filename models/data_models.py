class ChartDataSet:
    def __init__(self, dates, chart_data_list):
        self.dates = dates
        self.chart_data_list = chart_data_list


class ChartData:
    def __init__(self, name, values):
        self.name = name
        self.values = values


class TableData:
    def __init__(self, cols, headers, separate_bottom, data):
        self.cols = (cols,)
        self.headers = (headers,)
        self.separate_bottom = (separate_bottom,)
        self.data = data

    def to_dict(self):
        return {
            "cols": self.cols,
            "headers": self.headers,
            "separate-bottom": self.separate_bottom,
            "datapoints": self.data,
        }
