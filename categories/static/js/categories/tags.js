function statistics(url, renderTo) {
    var options = {
        chart: {
            renderTo: renderTo,
            zoomType: 'x'
        },
        title: {
            text: null
        },
        xAxis: {
            categories: [],
            crosshair: true
        },
        yAxis: {
            labels: {
                format: ''
            },
            plotLines: [{
                color: '#ff0000',
                value: 0,
                width: 1,
                zIndex: 1}
            ],
            stackLabels: {
                enabled: true,
                format: '',
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                },
            }
        },
        tooltip: {
            shared: true,
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
        options.tooltip.valueSuffix = data.tooltip.valueSuffix;
        options.xAxis.categories = data.xAxis.categories;
        options.xAxis.title = data.xAxis.title;
        options.yAxis.labels.format = data.yAxis.labels.format;
        options.yAxis.stackLabels.format = data.yAxis.stackLabels.format;
        options.yAxis.title = data.yAxis.title;
        var chart = new Highcharts.Chart(options);
    });
}
