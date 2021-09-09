var ectsCard = document.getElementById("ects-card-text");
var gradeCard = document.getElementById("grade-card-text");
var zscoreCard = document.getElementById("zscore-card-text");
var percentileCard = document.getElementById("percentile-card-text");
$.getJSON("js/agg_data.json", function(json) {
    ectsCard.textContent = json['total_ects'];
    gradeCard.textContent = json['avg_grade'].toFixed(2);
    zscoreCard.textContent = json['mean_z_score'].toFixed(2);
    percentileCard.textContent = json['avg_percentile'].toFixed(2) + "%";
});

