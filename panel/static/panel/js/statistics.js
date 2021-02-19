function draw_charts(data) {
    let ctx = document.getElementById('chart1').getContext('2d');

    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Нагрузка CPU',
                backgroundColor: "rgba(255, 99, 132, 0.5)",
                borderColor: "rgb(255, 99, 132)",
                fill: false,
                data: data,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'График CPU usage'
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Date'
                    },
                    ticks: {
                        major: {
                            fontStyle: 'bold',
                            fontColor: '#FF0000'
                        }
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'value'
                    }
                }]
            }
        }
    });
}