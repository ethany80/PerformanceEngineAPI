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


class Visualization:
    def __init__(self, width, height, x, y, request):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.request = request

    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
            "req": self.request,
        }
