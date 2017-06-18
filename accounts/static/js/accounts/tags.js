function tags(url, renderTo) {
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
            crosshair: true,
            title: {
                text: 'tags'
            }
        },
        yAxis: {
            title: {
                text: 'number of times used'
            },
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
        var chart = new Highcharts.Chart(options);
    });
}