# -*- coding: utf-8 -*-


def make_series(name, unit):
    return {
        'name': name,
        'colorByPoint': True,
        'dataLabels': {
            'enabled': True,
            'format': '{point.name}: {point.v:.%df} %s' % (unit.precision, unit.symbol)
        },
        'tooltip': {
            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.v:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
        },
        'data': []
    }


def make_drilldown(name, id, unit):
    return {
        'name': name,
        'id': id,
        'dataLabels': {
            'enabled': True,
            'format': '{point.name}: {point.v:.%df} %s' % (unit.precision, unit.symbol)
        },
        'tooltip': {
            'headerFormat': '<span style="font-size:11px">{series.name}</span><br>',
            'pointFormat': '<span style="color:{point.color}">{point.name}</span>: <b>{point.v:.%df} %s</b><br/>' % (unit.precision, unit.symbol)
        },
        'data': []
    }
