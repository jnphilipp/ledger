function statistics(url, renderTo) {
    var options = {
        chart: {
            renderTo: renderTo,
            type: 'column',
            zoomType: 'x'
        },
        title: {
            text: null
        },
        xAxis: {
            categories: [],
            crosshair: true,
            title: {
                text: ''
            }
        },
        yAxis: {
            title: {
                text: 'loss and profit'
            },
            labels: {
                format: ''
            },
            plotLines: [{
                value: 0,
                color: '#ff0000',
                width: 1,
                zIndex: 1}
            ],
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                },
                format: ''
            }
        },
        tooltip: {
            valueDecimals: 2,
            valueSuffix: ''
        },
        plotOptions: {
            column: {
                stacking: 'normal',
            }
        },
        series: [{}]
    };

    $.getJSON(url, function(data) {
        options.series = data.series;
        options.xAxis.categories = data.xAxis.categories;
        options.xAxis.title.text = data.xAxis.title;
        options.yAxis.labels.format = data.yAxis.labels.format;
        options.yAxis.stackLabels.format = data.yAxis.stackLabels.format;
        options.tooltip.valueSuffix = data.tooltip.valueSuffix;
        var chart = new Highcharts.Chart(options);
    });
}