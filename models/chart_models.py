class Bar:
    def __init__(self, dates, values):
        self.dates = dates
        self.values = values

    def to_dict(self):
        return {"x-axis": self.dates, "values": self.values}


class Line:
    def __init__(self, points):
        self.points = points

    def to_dict(self):
        return {"points": self.points}


class Pie:
    def __init__(self, slices):
        self.slices = slices

    def to_dict(self):
        return {"slices": self.slices}
