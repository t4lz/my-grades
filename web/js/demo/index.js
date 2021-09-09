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

$.getJSON("js/grade_data.json", function(grades) {
    let row = document.getElementById("bar-charts-row");
    let template = document.getElementById("template-bar-chart");
    let gradeStrs = ['1.0', '1.3', '1.7', '2.0', '2.3', '2.7', '3.0', '3.3', '3.7', '4.0', '4.3', '4.7', '5.0'];
    let gradeStrs4 = ['1.0', '1.3', '1.4', '1.7', '2.0', '2.3', '2.4', '2.7', '3.0', '3.3', '3.4', '3.7', '4.0', '4.3', '4.7', '5.0'];
    let charts = [];
    for (let i in grades) {
        let grade = grades[i];
        let newElement = template.cloneNode(true);
        let title = newElement.getElementsByTagName("h6")[0];
        title.textContent = grade['course_name_en'];
        charts.push(newElement);
        row.appendChild(newElement);
        let canvas = newElement.getElementsByTagName('canvas');
        let labels = grade['1.4'] || grade['2.4'] || grade['3.4'] ? gradeStrs4 : gradeStrs;
        let data = [];
        for (let label in labels) {
            data.push(grade[labels[label]]);
        }
        let chart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: "Number of students with grade",
                    backgroundColor: "#4e73df",
                    hoverBackgroundColor: "#2e59d9",
                    borderColor: "#4e73df",
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
