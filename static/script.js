const searchInput = document.getElementById("symptom-search");
const searchResults = document.getElementById("search-results");

const searchSection = document.getElementById("search-section");
const questionSection = document.getElementById("question-section");
const analyzingSection = document.getElementById("analyzing-section");
const resultSection = document.getElementById("result-section");

const questionText = document.getElementById("question-text");
const yesBtn = document.getElementById("yes-btn");
const noBtn = document.getElementById("no-btn");

const answeredCount = document.getElementById("answered-count");
const conditionsCount = document.getElementById("conditions-count");
const possibleConditions = document.getElementById("possible-conditions");
const statusText = document.getElementById("status-text");
const progressFill = document.getElementById("progress-fill");

const diseaseResult = document.getElementById("disease-result");
const matchPercentage = document.getElementById("match-percentage");
const matchProgressFill = document.getElementById("match-progress-fill");
const resultSymptoms = document.getElementById("result-symptoms");
const predictionReasons = document.getElementById("prediction-reasons");
const matchedSummary = document.getElementById("matched-summary");
let predictionExplanation = [];
const restartBtn = document.getElementById("restart-btn");


let yesSymptoms = [];
let noSymptoms = [];
let currentQuestion = null;
let analysisJourney = [];


// ==============================
// SEARCH SYMPTOMS
// ==============================

searchInput.addEventListener("input", async function () {

    const query = searchInput.value.trim();

    if (query.length === 0) {
        searchResults.innerHTML = "";
        return;
    }

    try {

        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);

        const data = await response.json();

        searchResults.innerHTML = "";

        data.symptoms.forEach(symptom => {

            const item = document.createElement("div");

            item.className = "search-result-item";

            item.textContent = symptom.replaceAll("_", " ");

            item.addEventListener("click", function () {

                startPrediction(symptom);

            });

            searchResults.appendChild(item);

        });

    } catch (error) {

        console.error("Search error:", error);

    }

});


// ==============================
// START PREDICTION
// ==============================

async function startPrediction(symptom) {

    searchResults.innerHTML = "";
    searchInput.value = symptom.replaceAll("_", " ");

    showAnalyzing("Analyzing your first symptom...");

    try {

        const response = await fetch("/start", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                symptom: symptom
            })

        });

        const data = await response.json();

        yesSymptoms = data.yes_symptoms || [];
        noSymptoms = data.no_symptoms || [];

        analysisJourney = [];

        analysisJourney.push({
            symptom: symptom,
            answer: "yes",
            candidateCount: data.candidate_count || 0
        });

        handleResponse(data);

    } catch (error) {

        console.error("Start error:", error);

    }

}


// ==============================
// ANSWER YES / NO
// ==============================

yesBtn.addEventListener("click", function () {

    submitAnswer("yes");

});


noBtn.addEventListener("click", function () {

    submitAnswer("no");

});


async function submitAnswer(answer) {

    if (!currentQuestion) return;

    showAnalyzing("Analyzing your symptoms...");

    try {

        const response = await fetch("/answer", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                yes_symptoms: yesSymptoms,
                no_symptoms: noSymptoms,
                symptom: currentQuestion,
                answer: answer

            })

        });

        const data = await response.json();

        const answeredSymptom = currentQuestion;

        yesSymptoms = data.yes_symptoms || [];
        noSymptoms = data.no_symptoms || [];

        analysisJourney.push({
            symptom: answeredSymptom,
            answer: answer,
            candidateCount: data.candidate_count || 0
        });

        handleResponse(data);

    } catch (error) {

        console.error("Answer error:", error);

    }

}


// ==============================
// HANDLE BACKEND RESPONSE
// ==============================

function handleResponse(data) {

    console.log(
    "BACKEND RESPONSE:",
    JSON.stringify(data, null, 2)
    );

    // Update possible conditions count
    if (data.candidate_count !== undefined) {
        conditionsCount.textContent = data.candidate_count;
    }
     if (possibleConditions) {
        updatePossibleConditions(data.conditions || []);
     }

    updateStatus();

    setTimeout(() => {

        if (data.status === "question") {

            currentQuestion = data.next_question;

            showQuestion(currentQuestion);

        }

        else if (data.status === "complete") {

            showResult(
                 data.disease,
                 data.match_percentage,
                 data.explanation || []
);

        }

        else if (data.status === "no_match") {

            alert("No matching condition found. Please try again.");

            restartApp();

        }

        else {

            alert("More information is needed.");

            restartApp();

        }

    }, 700);

}
// ==============================
// SHOW POSSIBLE CONDITIONS
// ==============================

function updatePossibleConditions(conditions) {

    possibleConditions.innerHTML = "";

    // If only one condition exists,
    // it is already shown on the LEFT side.
    if (!conditions || conditions.length <= 1) {
        return;
    }

    // Sort from highest score to lowest score
    const sortedConditions = [...conditions].sort(
        (a, b) => b.score - a.score
    );

    // Take maximum 3 conditions
    const topConditions = sortedConditions.slice(0, 3);

    // Highest condition is shown on LEFT side
    // So don't show it again on RIGHT side.
    const otherConditions = topConditions.slice(1);

    otherConditions.forEach(condition => {

        const conditionItem = document.createElement("div");
        conditionItem.className = "condition-item";

        const header = document.createElement("div");
        header.className = "condition-header";

        const diseaseName = document.createElement("div");
        diseaseName.className = "condition-name";

        diseaseName.textContent =
            condition.disease.replaceAll("_", " ");

        const score = document.createElement("span");
        score.className = "condition-score";

        score.textContent = condition.score + "%";

        header.appendChild(diseaseName);
        header.appendChild(score);

        const bar = document.createElement("div");
        bar.className = "condition-progress-bar";

        const fill = document.createElement("div");
        fill.className = "condition-progress-fill";

        fill.style.width = condition.score + "%";

        bar.appendChild(fill);

        conditionItem.appendChild(header);
        conditionItem.appendChild(bar);

        possibleConditions.appendChild(conditionItem);
    });
}

// ==============================
// SHOW QUESTION
// ==============================

function showQuestion(symptom) {

    analyzingSection.classList.add("hidden");

    searchSection.classList.add("hidden");

    questionSection.classList.remove("hidden");

    resultSection.classList.add("hidden");

    questionText.textContent =
        `Do you also have ${symptom.replaceAll("_", " ")}?`;

}


// ==============================
// SHOW ANALYZING
// ==============================

function showAnalyzing(text) {

    searchSection.classList.add("hidden");

    questionSection.classList.add("hidden");

    resultSection.classList.add("hidden");

    analyzingSection.classList.remove("hidden");

    document.getElementById("analyzing-text").textContent = text;

}

function showPredictionExplanation(explanation) {

    predictionReasons.innerHTML = "";

    if (!explanation || explanation.length === 0) {
        matchedSummary.textContent = "";
        return;
    }

    let matchedCount = 0;

    explanation.forEach(item => {

        const tag = document.createElement("span");

        if (item.status === "match") {

            tag.className = "prediction-reason yes";

            tag.textContent =
                "✓ " + item.symptom.replaceAll("_", " ");

            matchedCount++;

        } else {

            tag.className = "prediction-reason no";

            tag.textContent =
                "✕ " + item.symptom.replaceAll("_", " ");
        }

        predictionReasons.appendChild(tag);
    });

    matchedSummary.textContent =
        `${matchedCount} symptom${matchedCount !== 1 ? "s" : ""} support this prediction`;
}

// ==============================
// SHOW RESULT
// ==============================

function showResult(disease, score, explanation) {

    analyzingSection.classList.add("hidden");

    questionSection.classList.add("hidden");

    resultSection.classList.remove("hidden");

    diseaseResult.textContent = disease;

    const matchPercentageElement =
        document.getElementById("match-percentage");

    if (matchPercentageElement) {

    matchPercentageElement.textContent =
        score + "%";

    }

    const matchProgressFill =
        document.getElementById("match-progress-fill");

    if (matchProgressFill) {

         matchProgressFill.style.width =
             score + "%";

    }

    resultSymptoms.innerHTML = "";

    yesSymptoms.forEach(symptom => {

        const tag = document.createElement("span");

        tag.className = "symptom-tag";

        tag.textContent =
            symptom.replaceAll("_", " ");

        resultSymptoms.appendChild(tag);

    });

    statusText.textContent = "Analysis complete";

    progressFill.style.width = "100%";

    showPredictionExplanation(explanation);

}


// ==============================
// UPDATE STATUS PANEL
// ==============================

function updateStatus() {

    const totalAnswered =
        yesSymptoms.length + noSymptoms.length;

    answeredCount.textContent = totalAnswered;

    const progress = Math.min(totalAnswered * 15, 90);

    progressFill.style.width = progress + "%";

    statusText.textContent =
        "Analyzing your symptom information...";

}

function restartApp() {

    yesSymptoms = [];

    noSymptoms = [];

    currentQuestion = null;

    analysisJourney = [];

    searchInput.value = "";

    searchResults.innerHTML = "";

    resultSection.classList.add("hidden");

    questionSection.classList.add("hidden");

    analyzingSection.classList.add("hidden");

    searchSection.classList.remove("hidden");

    answeredCount.textContent = "0";

    conditionsCount.textContent = "0";

    statusText.textContent =
        "Waiting for your first symptom";

    progressFill.style.width = "0%";

    possibleConditions.innerHTML =
    `<p class="empty-text">No conditions identified yet.</p>`;

}

// ==============================
// ANALYSIS JOURNEY
// ==============================

const journeyBtn = document.getElementById("journey-btn");
const journeyModal = document.getElementById("journey-modal");
const closeJourney = document.getElementById("close-journey");
const journeyTimeline = document.getElementById("journey-timeline");


journeyBtn.addEventListener("click", function () {

    journeyTimeline.innerHTML = "";

    analysisJourney.forEach((step, index) => {

        const stepBox = document.createElement("div");
        stepBox.className = "journey-step";

        const answerClass =
            step.answer === "yes" ? "yes" : "no";

        const answerText =
            step.answer === "yes" ? "YES ✓" : "NO ✕";

        stepBox.innerHTML = `
            <div class="journey-number">
                ${index + 1}
            </div>

            <div class="journey-step-content">

                <h3>
                    ${step.symptom.replaceAll("_", " ")}
                </h3>

                <span class="journey-answer ${answerClass}">
                    ${answerText}
                </span>

                <p>
                    ${step.candidateCount}
                    possible condition${step.candidateCount !== 1 ? "s" : ""}
                </p>

            </div>
        `;

        journeyTimeline.appendChild(stepBox);

        if (index < analysisJourney.length - 1) {

            const line = document.createElement("div");

            line.className = "journey-line";

            journeyTimeline.appendChild(line);

        }

    });
        // ==============================
    // FINAL PREDICTION
    // ==============================

    const finalResult = document.createElement("div");

    finalResult.className = "journey-final-result";

    finalResult.innerHTML = `
        <div class="journey-final-icon">
            🎯
        </div>

        <p class="journey-final-label">
            FINAL AI ANALYSIS
        </p>

        <h2>
            ${diseaseResult.textContent}
        </h2>

        <strong>
            ${matchPercentage.textContent} Match
        </strong>

        <p>
            Based on the symptoms and answers provided.
        </p>
    `;

    journeyTimeline.appendChild(finalResult);


    // ==============================
    // WHAT CHANGED THE ANALYSIS
    // ==============================

    const analysisSummary = document.createElement("div");

    analysisSummary.className = "analysis-summary";

    analysisSummary.innerHTML = `
        <h3>🔍 What changed the analysis?</h3>

        <p>
        Your answers helped the AI narrow down the possible conditions.
        </p>

        <div class="analysis-summary-list"></div>
`;

    const summaryList =
        analysisSummary.querySelector(".analysis-summary-list");

    analysisJourney.forEach(step => {

        const item = document.createElement("div");

        item.className =
            step.answer === "yes"
                ? "summary-item yes"
                : "summary-item no";

        item.innerHTML = `
            <span class="summary-icon">
                ${step.answer === "yes" ? "✓" : "✕"}
            </span>

            <span>
                ${step.symptom.replaceAll("_", " ")}
            </span>

            <strong>
                ${step.answer === "yes" ? "Supported" : "Not present"}
            </strong>
    `     ;

        summaryList.appendChild(item);

    });

    journeyTimeline.appendChild(analysisSummary);

    journeyModal.classList.remove("hidden");

});


closeJourney.addEventListener("click", function () {

    journeyModal.classList.add("hidden");

});


journeyModal.addEventListener("click", function (event) {

    if (event.target === journeyModal) {

        journeyModal.classList.add("hidden");

    }

});
