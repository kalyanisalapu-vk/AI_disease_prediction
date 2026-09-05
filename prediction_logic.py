import pandas as pd
import joblib
from pathlib import Path


# ==========================
# LOAD DATA AND MODEL
# ==========================

BASE_DIR = Path(__file__).resolve().parent

data = pd.read_csv(BASE_DIR / "Training.csv")

if "Unnamed: 133" in data.columns:
    data = data.drop(columns=["Unnamed: 133"])

model = joblib.load(BASE_DIR / "disease_model.pkl")
all_symptoms = joblib.load(BASE_DIR / "symptoms.pkl")


# ==========================
# FILTER DISEASES
# ==========================

def filter_diseases(yes_symptoms, no_symptoms):

    filtered_data = data.copy()

    # YES symptoms must be present
    for symptom in yes_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 1
        ]

    # NO symptoms must be absent
    for symptom in no_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 0
        ]

    return filtered_data


# ==========================
# DISEASE SCORING
# ==========================

def calculate_disease_scores(
    yes_symptoms,
    no_symptoms,
    possible_diseases=None
):

    disease_scores = []

    if possible_diseases is None:
        possible_diseases = data["prognosis"].unique()

    total_answers = (
        len(yes_symptoms) +
        len(no_symptoms)
    )

    if total_answers == 0:
        return []

    for disease_name in possible_diseases:

        disease_rows = data[
            data["prognosis"] == disease_name
        ]

        if disease_rows.empty:
            continue

        disease_row = disease_rows.iloc[0]

        matched_answers = 0

        # Check YES symptoms
        for symptom in yes_symptoms:

            if disease_row[symptom] == 1:
                matched_answers += 1

        # Check NO symptoms
        for symptom in no_symptoms:

            if disease_row[symptom] == 0:
                matched_answers += 1

        match_percentage = (
            matched_answers / total_answers
        ) * 100

        disease_scores.append({
            "disease": disease_name,
            "score": round(match_percentage, 1)
        })

    disease_scores.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return disease_scores


# ==========================
# GET BEST NEXT QUESTION
# ==========================

def get_best_question(filtered_data, asked_symptoms):

    if filtered_data.empty:
        return None

    possible_diseases = (
        filtered_data["prognosis"].unique()
    )

    remaining_symptoms = [
        symptom
        for symptom in all_symptoms
        if symptom not in asked_symptoms
    ]

    # Multiple diseases remaining
    if len(possible_diseases) > 1:

        best_symptom = None
        best_score = -1

        for symptom in remaining_symptoms:

            yes_count = (
                filtered_data[symptom] == 1
            ).sum()

            no_count = (
                filtered_data[symptom] == 0
            ).sum()

            if yes_count == 0 or no_count == 0:
                continue

            score = min(
                yes_count,
                no_count
            )

            if score > best_score:
                best_score = score
                best_symptom = symptom

        return best_symptom

    # One disease remaining
    if len(possible_diseases) == 1:

        disease_name = possible_diseases[0]

        disease_rows = data[
            data["prognosis"] == disease_name
        ]

        for symptom in remaining_symptoms:

            if disease_rows[symptom].sum() > 0:
                return symptom

    return None


# ==========================
# SEARCH SYMPTOMS
# ==========================

def search_symptoms(search_text):

    search_text = search_text.strip().lower()

    if not search_text:
        return []

    search_clean = search_text.replace(
        " ",
        "_"
    )

    matches = [
        symptom
        for symptom in all_symptoms
        if search_clean in symptom
        or search_text in symptom.replace("_", " ")
    ]

    return matches


# ==========================
# GET PREDICTION
# ==========================

def get_prediction(yes_symptoms, no_symptoms):

    # Filter using BOTH YES and NO answers
    filtered_data = filter_diseases(
        yes_symptoms,
        no_symptoms
    )

    # No disease matches all answers
    if filtered_data.empty:

        return {
            "status": "no_match",
            "disease": None,
            "match_percentage": 0,
            "next_question": None,
            "candidate_count": 0,
            "conditions": [],
            "explanation": []
        }

    # Get only currently possible diseases
    possible_diseases = (
        filtered_data["prognosis"].unique()
    )

    # Calculate scores ONLY for possible diseases
    disease_scores = calculate_disease_scores(
        yes_symptoms,
        no_symptoms,
        possible_diseases
    )

    if not disease_scores:

        return {
            "status": "no_match",
            "disease": None,
            "match_percentage": 0,
            "next_question": None,
            "candidate_count": 0,
            "conditions": [],
            "explanation": []
        }

    # Best disease MUST come from possible conditions
    best_match = disease_scores[0]

    predicted_disease = best_match["disease"]
    match_percentage = best_match["score"]

    candidate_count = len(possible_diseases)

    # Keep top 3 possible conditions
    possible_conditions = disease_scores[:3]

    # ==========================
    # EXPLANATION
    # ==========================

    predicted_rows = data[
        data["prognosis"] == predicted_disease
    ]

    predicted_row = predicted_rows.iloc[0]

    explanation = []

    for symptom in yes_symptoms:

        explanation.append({
            "symptom": symptom,
            "status": "yes"
        })

    for symptom in no_symptoms:

        explanation.append({
            "symptom": symptom,
            "status": "no"
        })

    asked_symptoms = (
        yes_symptoms +
        no_symptoms
    )

    next_question = get_best_question(
        filtered_data,
        asked_symptoms
    )

    total_answers = len(asked_symptoms)

    # ==========================
    # COMPLETE
    # ==========================

    if total_answers >= 5:

        return {
            "status": "complete",
            "disease": predicted_disease,
            "match_percentage": match_percentage,
            "next_question": None,
            "candidate_count": candidate_count,
            "conditions": possible_conditions,
            "explanation": explanation
        }

    # ==========================
    # CONTINUE QUESTIONS
    # ==========================

    if next_question is not None:

        return {
            "status": "question",
            "disease": None,
            "match_percentage": match_percentage,
            "next_question": next_question,
            "candidate_count": candidate_count,
            "conditions": possible_conditions,
            "explanation": explanation
        }

    # ==========================
    # NO MORE QUESTIONS
    # ==========================

    return {
        "status": "complete",
        "disease": predicted_disease,
        "match_percentage": match_percentage,
        "next_question": None,
        "candidate_count": candidate_count,
        "conditions": possible_conditions,
        "explanation": explanation
    }