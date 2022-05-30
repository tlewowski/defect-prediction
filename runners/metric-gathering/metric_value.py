

class MetricValue:
    metric: str
    entity: str
    value: any

    def __init__(self, metric: str, entity: str, value: any):
        self.metric = metric
        self.entity = entity
        self.value = value

    def as_tuple(self):
        return self.metric, self.entity, self.value