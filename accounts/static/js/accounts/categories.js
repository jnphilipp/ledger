function categories(url, renderTo) {
    var options = {
        chart: {
            renderTo: renderTo,
            type: 'column',
            zoomType: 'x'
        },
        legend: {
            enabled: false
        },
        title: {
            text: null
        },
        xAxis: {
            categories: [],
            crosshair: true
        },
        yAxis: {
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
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
        options.xAxis.title = data.xAxis.title;
        options.yAxis.title = data.yAxis.title;
        var chart = new Highcharts.Chart(options);
    });
}
