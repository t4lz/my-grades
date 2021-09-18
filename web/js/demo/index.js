let gradeStrs = ['1.0', '1.3', '1.7', '2.0', '2.3', '2.7', '3.0', '3.3', '3.7', '4.0', '4.3', '4.7', '5.0'];
let gradeStrs4 = ['1.0', '1.3', '1.4', '1.7', '2.0', '2.3', '2.4', '2.7', '3.0', '3.3', '3.4', '3.7', '4.0', '4.3', '4.7', '5.0'];
let ectsCard = document.getElementById("ects-card-text");
let gradeCard = document.getElementById("grade-card-text");
let zscoreCard = document.getElementById("zscore-card-text");
let percentileCard = document.getElementById("percentile-card-text");
$.getJSON("js/agg_data.json", function(json) {
    ectsCard.textContent = json['total_ects'];
    gradeCard.textContent = json['avg_grade'].toFixed(2);
    zscoreCard.textContent = json['mean_z_score'].toFixed(2);
    percentileCard.textContent = json['avg_percentile'].toFixed(2) + "%";
});

$.getJSON("js/semester_data.json", function(semesterData) {
    let canvas = document.getElementById("semester-linechart-canvas");
    let datasets = [];
    let yAxes = [];
    let labels;
    let colors = [
        "#00796B",
        "#FFC107",
        "#B2DFDB",
        "#757575",
        "#E64A19",
    ];
    let colorIndex = 0;
    for (let key in semesterData) {
        if (key === "semester_code") {
            labels = semesterData[key];
        } else {
            color = colors[colorIndex++];
            datasets.push({label: key, data: semesterData[key], yAxisID: key, fill: false,
                backgroundColor: color,
                borderColor: color,
            });
            yAxes.push({
                id: key,
                type: 'linear',
                display: false,
                stacked: false,
                gridLines: {
                    display: false
                },

            });
        }
    }
    let chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            maintainAspectRatio: false,
            stacked: false,
            // layout: {
            //     padding: {
            //         left: 10,
            //         right: 25,
            //         top: 25,
            //         bottom: 0
            //     }
            // },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                }],
                yAxes: yAxes,
            },
            legend: {
                display: true
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        let y = tooltipItem.yLabel;
                        let label = data.datasets[tooltipItem.datasetIndex].label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += y % 1 === 0 ? y : y.toFixed(2);
                        return label;
                    }
                }

            },
        }
    });
});

$.getJSON("js/grade_data.json", function(grades) {
    let row = document.getElementById("bar-charts-row");
    let template = document.getElementById("template-bar-chart");
    let charts = [];
    for (let i in grades) {
        let grade = grades[i];
        let myGrade = grade['grade'];
        let newElement = template.cloneNode(true);
        let title = newElement.getElementsByClassName("course-name")[0];
        title.textContent = grade['course_name_en'];
        let gradeDiv = newElement.getElementsByClassName("course-grade")[0];
        gradeDiv.textContent = myGrade;
        let ectsDiv = newElement.getElementsByClassName("ects-text")[0];
        ectsDiv.textContent = grade['ects'] + " ECTS";
        let sememesterDiv = newElement.getElementsByClassName("semester-text")[0];
        sememesterDiv.textContent = grade['semester_name_en'];
        let zDiv = newElement.getElementsByClassName("z-score-text")[0];
        zDiv.textContent = "Z-Score: " + grade['z'].toFixed(2);
        let percentileDiv = newElement.getElementsByClassName("percentile-text")[0];
        percentileDiv.textContent = grade['percentile'].toFixed(2) + " percentile";
        charts.push(newElement);
        row.appendChild(newElement);
        let canvas = newElement.getElementsByTagName('canvas');
        let labels = grade['1.4'] || grade['2.4'] || grade['3.4'] ? gradeStrs4 : gradeStrs;
        let myGradeIndex = labels.indexOf(myGrade);
        let data = [];
        for (let label in labels) {
            data.push(grade[labels[label]]);
        }
        let colors = Array(labels.length).fill("#adb5bd");
        colors[myGradeIndex] = "#20c997";
        let hoverColors = Array(labels.length).fill("#B2DFDB");
        hoverColors[myGradeIndex] = "#17a2b8";
        let chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: "Number of students with grade",
                    // backgroundColor: "#4e73df",
                    // hoverBackgroundColor: "#2e59d9",
                    // borderColor: "#4e73df",
                    backgroundColor: colors,
                    hoverBackgroundColor: hoverColors,
                    borderColor: "#0065BD",
                    data: data,
                }],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                    }],
                },
                legend: {
                    display: false
                },
                tooltips: {
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                },
            }
        });
    }
    template.remove();
});

$.getJSON("js/personal_distribution.json", function(dist) {
        let canvas = document.getElementById('personal-distribution-barchart-canvas');
        let labels = gradeStrs;
        let colors = Array(labels.length).fill("#20c997");
        let hoverColors = Array(labels.length).fill("#17a2b8");
        let chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: "Relative part of this grade",
                    // backgroundColor: "#4e73df",
                    // hoverBackgroundColor: "#2e59d9",
                    // borderColor: "#4e73df",
                    backgroundColor: colors,
                    hoverBackgroundColor: hoverColors,
                    borderColor: "#0065BD",
                    data: dist,
                }],
            },
            options: {
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                    }],
                },
                legend: {
                    display: false
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            let label = data.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += tooltipItem.yLabel.toFixed(2);
                            return label;
                        }
                    }

                },
            }
        });
});
