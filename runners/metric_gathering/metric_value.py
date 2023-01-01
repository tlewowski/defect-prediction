
class MetricValue:
    metric: str
    entity: str
    value: any

    def __init__(self, metric: str, entity: str, value: any):
        self.metric = metric
        self.entity = entity
        self.value = value

    def as_tuple(self):
        return self.metric.encode("utf-8"), self.entity.encode("utf-8"), str(self.value).encode("utf-8")