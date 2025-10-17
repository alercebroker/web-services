import { customToolTip } from "./customToolTip.js"


export function get_radar_config(){
    let config = 
    {
        type: 'radar',
        data: get_initial_config_data(),
        options: {
            responsive: true,
            maintainAspectRatio: false,
            pointRadius: 5,
            elements: {
                line: {
                    borderWidth: 1,
                    fill: true,
                }
            },
            scales: {
                r: {
                    backgroundColor: 'rgba(245, 245, 245, 0.2)',
                    ticks: {
                        display: false,
                        stepSize: 0.33,
                    },
                    angleLines: {
                        color: '#F5F5F5'
                    },
                    grid: {
                        color: '#F5F5F5',
                    },
                    pointLabels: {
                        color: '#F5F5F5',
                        font: {
                            size: 14
                        }
                    },
                    beginAtZero: true,
                    max: 1
                },
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false,
                    mode: 'dataset',
                    position: 'nearest',
                    external: customToolTip,
                }
            },

        }
    }

    return config
}

function get_initial_config_data(){
    let data = {
        labels: [],
        datasets: [{
            label: 'Probabilities',
            data: [],
            fill: true,
            backgroundColor: 'rgba(255, 0, 54, 0.7)',
            borderColor: 'rgb(255, 0, 54)',
            pointBackgroundColor: 'rgb(255, 0, 54)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(255, 0, 54)',
        }]
    };

    return data
}