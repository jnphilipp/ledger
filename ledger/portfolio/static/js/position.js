function position(url, renderTo) {
    $.getJSON(url, function(data) {
        data.series.forEach(function(entry) {
            entry.data.forEach(function(d) {d[0]=Date.parse(d[0]);});
            if ( entry.name == 'Spread' )
                entry.color = Highcharts.getOptions().colors[0];
        });

        var $container = $('#'+renderTo);
        $('<div id="detail-container">').css({
            'height': $container.height() - 100,
            'width': '100%'
        }).appendTo($container);
        $('<div id="master-container">').css({
            height: 100,
            width: '100%'
        }).appendTo($container);

        function createDetail(masterChart) {
            var detailSeries = [],
                start = data.series[0].data.length > 260 ? data.series[0].data[data.series[0].data.length - 261][0] : data.series[0].data[0][0];
            masterChart.series.forEach(function(s, i) {
                detailSeries[i] = data.series[i];
                detailSeries[i].data = [];
                s.data.forEach(function(d) {
                    if ( start <= d.x ) {
                        if ( 'high' in d && 'low' in d ) {
                            detailSeries[i].data.push([d.x, d.high, d.low]);
                        }
                        else {
                            detailSeries[i].data.push([d.x, d.y]);
                        }
                    }
                });
            });

            detailChart = $('#detail-container').highcharts({
                chart: {
                    reflow: false
                },
                legend: {
                    enabled: true
                },
                title: {
                    text: null
                },
                tooltip: {
                    crosshairs: true,
                    shared: true,
                    valueDecimals: 3,
                    valueSuffix: ''
                },
                xAxis: {
                    crosshair: true,
                    title: {
                        text: data.yAxis.title
                    },
                    type: 'datetime'
                },
                yAxis: {
                    labels: {
                        format: ''
                    },
                    title: {
                        text: 'Stock price'
                    }
                },
                series: detailSeries,
            }).highcharts();
        }

        function createMaster() {
            $('#master-container').highcharts({
                chart: {
                    reflow: false,
                    borderWidth: 0,
                    backgroundColor: null,
                    marginLeft: 50,
                    marginRight: 20,
                    zoomType: 'x',
                    events: {
                        selection: function (event) {
                            var extremesObject = event.xAxis[0],
                                min = extremesObject.min,
                                max = extremesObject.max,
                                xAxis = this.xAxis[0];
                            this.series.forEach(function(s, i) {
                                data = [];
                                s.data.forEach(function(d) {
                                    if ( d.x > min && d.x < max ) {
                                        if ( 'high' in d && 'low' in d ) {
                                            data.push([d.x, d.high, d.low]);
                                        }
                                        else {
                                            data.push([d.x, d.y]);
                                        }
                                    }
                                });
                                detailChart.series[i].setData(data);
                            });
                            xAxis.removePlotBand('mask');
                            xAxis.addPlotBand({
                                id: 'mask',
                                from: min,
                                to: max,
                                color: 'rgba(0, 0, 0, 0.2)'
                            });
                            return false;
                        }
                    }
                },
                credits: {
                    enabled: false
                },
                exporting: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
                title: {
                    text: null
                },
                tooltip: {
                    formatter: function () {
                        return false;
                    }
                },
                xAxis: {
                    type: 'datetime',
                    showLastTickLabel: true,
                    plotBands: [{
                        id: 'mask',
                        from: data.series[0].data.length > 260 ? data.series[0].data[data.series[0].data.length - 261][0] : data.series[0].data[0][0],
                        to: data.series[0].data[data.series[0].data.length - 1][0],
                        color: 'rgba(0, 0, 0, 0.2)'
                    }],
                    title: {
                        text: null
                    }
                },
                yAxis: [{
                    gridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: null
                    },
                    showFirstLabel: false
                }, {
                    gridLineWidth: 0,
                    opposite: true,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: null
                    },
                    showFirstLabel: false,
                }],
                plotOptions: {
                    series: {
                        lineWidth: 1,
                        marker: {
                            enabled: false
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        },
                        enableMouseTracking: false
                    }
                },
                series: data.series
            }, function (masterChart) {
                createDetail(masterChart);
            }).highcharts();
        }

        createMaster();
    });
}
