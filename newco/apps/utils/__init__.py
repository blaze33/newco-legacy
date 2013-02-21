from django.db.models import aggregates
from django.db.models.sql import aggregates as sql_aggregates


class SumWithDefault(aggregates.Aggregate):
    name = 'SumWithDefault'


class SQLSumWithDefault(sql_aggregates.Sum):
    sql_template = 'COALESCE(%(function)s(%(field)s), %(default)s)'

setattr(sql_aggregates, 'SumWithDefault', SQLSumWithDefault)
