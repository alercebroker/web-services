const htmx = window.htmx;

const buttons = {
    oidSearch: document.getElementById("btnOidSearch"),
    scoreSearch: document.getElementById("btnScoreSearch"),
    scoreClear: document.getElementById("btnScoreClear"),
    multipleScoreSearch: document.getElementById("btnMultipleScoreSearch"),
    multipleScoreClear: document.getElementById("btnMultipleScoreClear"),
    probabilitySearch: document.getElementById("btnProbabilitySearch"),
    probabilityClear: document.getElementById("btnProbabilityClear")
}

const inputs = {
    object: {
        oid: document.getElementById("inputOid"),
    },
    score: {
        ndetMin: document.getElementById("inputNdetMin"),
        ndetMax: document.getElementById("inputNdetMax"),
        scoreMin: document.getElementById("inputScoreMin"),
        scoreMax: document.getElementById("inputScoreMax"),
        percentilMin: document.getElementById("inputPercentilMin"),
        percentilMax: document.getElementById("inputPercentilMax"),
    },
    multipleScore: {
        ndetMin: document.getElementById("inputMultipleNdetMin"),
        ndetMax: document.getElementById("inputMultipleNdetMax"),
        scoreMin: document.getElementById("inputMultipleScoreMin"),
        scoreMax: document.getElementById("inputMultipleScoreMax"),
        percentilMin: document.getElementById("inputMultiplePercentilMin"),
        percentilMax: document.getElementById("inputMultiplePercentilMax"),
    },
    multipleScoreStochastic: {
        scoreMin: document.getElementById("inputMultipleStochasticScoreMin"),
        scoreMax: document.getElementById("inputMultipleStochasticScoreMax"),
        percentilMin: document.getElementById("inputMultipleStochasticPercentilMin"),
        percentilMax: document.getElementById("inputMultipleStochasticPercentilMax"),
    },
    multipleScorePeriodic: {
        scoreMin: document.getElementById("inputMultiplePeriodicScoreMin"),
        scoreMax: document.getElementById("inputMultiplePeriodicScoreMax"),
        percentilMin: document.getElementById("inputMultiplePeriodicPercentilMin"),
        percentilMax: document.getElementById("inputMultiplePeriodicPercentilMax"),
    },
    probability: {
        ndetMin: document.getElementById("inputProbabilityNdetMin"),
        ndetMax: document.getElementById("inputProbabilityNdetMax"),
        scoreMin: document.getElementById("inputProbabilityScoreMin"),
        scoreMax: document.getElementById("inputProbabilityScoreMax"),
        percentilMin: document.getElementById("inputProbabilityPercentilMin"),
        percentilMax: document.getElementById("inputProbabilityPercentilMax"),
    }
}

function oidQueryParams() {
    const oids_str = inputs.object.oid.value;
    if (oids_str === "") {
        return ""
    }
    const oids = oids_str.split(",");
    return `objectId=${oids.join("&objectId=")}`;
}

function pagingQueryParams(page, per_page) {
    if (!Number.isInteger(page) || !Number.isInteger(per_page)) {
        return ""
    }
    return `page=${page}&per_page=${per_page}`
}

export function buildTableUrl(page = 0, per_page = 10) {
    const queryParams = [];
    if (inputs.object.oid.value !== "") {
        queryParams.push(oidQueryParams())
    }
    if (Number.isInteger(page) && Number.isInteger(per_page)) {
        queryParams.push(pagingQueryParams(page, per_page))
    }

    if (queryParams.length === 0) {
        return "/tabla"
    }
    return `/tabla?${queryParams.join("&")}`
}

buttons.oidSearch.addEventListener("click", async () => {
    await htmx.ajax("GET", buildTableUrl(), { target: "#tableContainer", swap: "innerHTML" });
})

// const buttonMappings = [
//     { buttonId: "btnOidSearch", containerId: "inputOidContainer" },
//     { buttonId: "scoreSearchBtn", containerId: "scoreFormContainer" },
//     { buttonId: "multipleScoreSearchBtn", containerId: "multipleFormContainer" },
//     { buttonId: "probabilitySearchBtn", containerId: "probabilityFormContainer" }
// ];
//
// const inputsMultipleMappings = [
//     { scoreId: "minMultipleTransientScore", percentilId: "minMultipleTransientPercentil", category: "transient" },
//     { scoreId: "maxMultipleTransientScore", percentilId: "maxMultipleTransientPercentil", category: "transient" },
//     { scoreId: "minMultipleStochasticScore", percentilId: "minMultipleStochasticPercentil", category: "stochastic" },
//     { scoreId: "maxMultipleStochasticScore", percentilId: "maxMultipleStochasticPercentil", category: "stochastic" },
//     { scoreId: "minMultiplePeriodicScore", percentilId: "minMultiplePeriodicPercentil", category: "periodic" },
//     { scoreId: "maxMultiplePeriodicScore", percentilId: "maxMultiplePeriodicPercentil", category: "periodic" },
//     { scoreId: "minScore", percentilId: "minPercentil", category: "Category" },
//     { scoreId: "maxScore", percentilId: "maxPercentil", category: "Category" },
//     { scoreId: "minProbabilityScore", percentilId: "minProbabilityPercentil", category: "CategoryProbability" },
//     { scoreId: "maxProbabilityScore", percentilId: "maxProbabilityPercentil", category: "CategoryProbability" },
// ];
//
// buttonMappings.forEach((element) => {
//     document.getElementById(element.buttonId).addEventListener("click", () => {
//         handleVisibility(element.containerId);
//     })
// })
//
// inputsMultipleMappings.forEach(({ scoreId, percentilId, category }) => {
//     let scoreInput = document.getElementById(scoreId);
//     let percentilInput = document.getElementById(percentilId);
//
//     scoreInput.addEventListener("change", () => {
//         parse_score_to_percentil(scoreInput.value, percentilId, category)
//     });
//
//     percentilInput.addEventListener("change", () => {
//         parse_percentil_to_score(percentilInput.value, scoreId, category)
//     })
// })
//
// // functions start
//
// function parse_percentil_to_score(percentil_id, target_id, category_id) {
//
//     if (checkSelectElement(category_id)) {
//         let category = document.getElementById(category_id)
//         if (category.value == "") {
//             return false;
//         } else {
//             document.getElementById(target_id).value = 10;
//             return 10;
//         }
//     } else {
//         if (category_id == "" || category_id == "Category" || category_id == "CategoryProbability") {
//             return false;
//         } else {
//             document.getElementById(target_id).value = 10;
//             return 10;
//         }
//     }
// }
//
// function parse_score_to_percentil(score, target_id, category_id) {
//
//     if (checkSelectElement(category_id)) {
//         let category = document.getElementById(category_id)
//         if (category.value == "") {
//             return false;
//         } else {
//             document.getElementById(target_id).value = 65;
//             return 65;
//         }
//     } else {
//         if (category_id == "" || category_id == "Category" || category_id == "CategoryProbability") {
//             return false;
//         } else {
//             document.getElementById(target_id).value = 65;
//             return 65;
//         }
//     }
// }
//
// function checkSelectElement(element) {
//     if (document.getElementById(element) != null) {
//         return true;
//     } else {
//         return false;
//     }
// }
//
// function handleVisibility(id) {
//     let element = document.getElementById(id);
//     element.classList.toggle("tw-hidden");
// }


// multiple functions
/*

const inputsForm = [
    { scoreId: "minScore", percentilId: "minPercentil", category_id: "Category"},
    { scoreId: "maxScore", percentilId: "maxPercentil", category_id: "Category"},
    { scoreId: "minProbabilityScore", percentilId: "minProbabilityPercentil", category_id: "CategoryProbability"},
    { scoreId: "maxProbabilityScore", percentilId: "maxProbabilityPercentil", category_id: "CategoryProbability"},
];

inputsForm.forEach(({scoreId, percentilId, category_id}) => {
    let scoreInputForm = document.getElementById(scoreId);
    let percentilInputForm = document.getElementById(percentilId);

    scoreInputForm.addEventListener("change", () => {
        parse_score_to_percentil(scoreInputForm.value, percentilId, category_id)
    });

    percentilInputForm.addEventListener("change", () => {
        parse_percentil_to_score(percentilInputForm.value, scoreId, category_id)
    })
})

function parse_percentil_to_score_multiple(percentil_id, target_id, category_id) {
    if(category_id == ""){
        return false;
    } else {
        document.getElementById(target_id).value = 10;
        return 10;
    }
}

function parse_score_to_percentil_multiple(score, target_id, category_id) {
    if(category_id == ""){
        return false;
    } else {
        document.getElementById(target_id).value = 65;
        return 65;
    }
}
*/


/*
function parse_percentil_to_score(percentil_id, target_id, category_id) {
    let category = document.getElementById(category_id)

    if(category.value == ""){
        return false;
    } else {
        document.getElementById(target_id).value = 10;
        return 10;
    }
}

function parse_score_to_percentil(score, target_id, category_id) {
    let category = document.getElementById(category_id)
    if(category.value == ""){
        return false;
    } else {
        document.getElementById(target_id).value = 65;
        return 65;
    }
}
*/
