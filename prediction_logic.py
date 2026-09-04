import pandas as pd
import joblib
from pathlib import Path


# ==========================
# LOAD DATA AND MODEL
# ==========================

BASE_DIR = Path(__file__).resolve().parent

data = pd.read_csv(BASE_DIR / "Training.csv")

# Remove unnecessary column
if "Unnamed: 133" in data.columns:
    data = data.drop(columns=["Unnamed: 133"])

model = joblib.load(BASE_DIR / "disease_model.pkl")
all_symptoms = joblib.load(BASE_DIR / "symptoms.pkl")


# ==========================
# FILTER DISEASES
# ==========================

def filter_diseases(yes_symptoms, no_symptoms):
    """
    Filters diseases based mainly on YES symptoms.
    """

    filtered_data = data.copy()

    # Keep rows matching all YES symptoms
    for symptom in yes_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 1
        ]

    return filtered_data


# ==========================
# DISEASE SCORING
# ==========================

def calculate_disease_scores(yes_symptoms, no_symptoms):
    """
    Calculate how well each disease matches
    the user's YES and NO symptom answers.
    """

    disease_scores = []

    for disease_name in data["prognosis"].unique():

        disease_rows = data[
            data["prognosis"] == disease_name
        ]

        # Get one representative symptom row
        disease_row = disease_rows.iloc[0]

        total_answers = (
            len(yes_symptoms) +
            len(no_symptoms)
        )

        if total_answers == 0:
            continue

        matched_answers = 0

        # Check YES symptoms
        for symptom in yes_symptoms:

            if disease_row[symptom] == 1:
                matched_answers += 1

        # Check NO symptoms
        for symptom in no_symptoms:

            if disease_row[symptom] == 0:
                matched_answers += 1

        # Calculate match percentage
        match_percentage = (
            matched_answers / total_answers
        ) * 100

        disease_scores.append({
            "disease": disease_name,
            "score": match_percentage
        })

    # Highest match first
    disease_scores.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return disease_scores


# ==========================
# GET BEST NEXT QUESTION
# ==========================

def get_best_question(filtered_data, asked_symptoms):
    """
    Finds the next useful symptom question.
    """

    possible_diseases = (
        filtered_data["prognosis"].unique()
    )

    remaining_symptoms = [
        symptom
        for symptom in all_symptoms
        if symptom not in asked_symptoms
    ]

    # --------------------------------
    # MULTIPLE DISEASES REMAINING
    # --------------------------------

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

            # Skip useless questions
            if yes_count == 0 or no_count == 0:
                continue

            # Balanced question is better
            score = min(
                yes_count,
                no_count
            )

            if score > best_score:
                best_score = score
                best_symptom = symptom

        return best_symptom

    # --------------------------------
    # ONLY ONE DISEASE REMAINING
    # ASK CONFIRMATION SYMPTOMS
    # --------------------------------

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
# GET CURRENT PREDICTION
# ==========================

def get_prediction(yes_symptoms, no_symptoms):

    disease_scores = calculate_disease_scores(
        yes_symptoms,
        no_symptoms
    )

    if not disease_scores:
        return {
            "status": "no_match",
            "disease": None,
            "match_percentage": 0,
            "next_question": None,
            "candidate_count": 0,
            "conditions": []
        }

    # Filter diseases based on YES symptoms
    filtered_data = filter_diseases(
        yes_symptoms,
        no_symptoms
    )

    possible_diseases = filtered_data["prognosis"].unique()

    # Create possible conditions with scores
    possible_conditions = [
        item
        for item in disease_scores
        if item["disease"] in possible_diseases
    ]

    # Round scores
    for item in possible_conditions:
        item["score"] = round(item["score"], 1)

    # Best overall match
    best_match = disease_scores[0]

    predicted_disease = best_match["disease"]

    predicted_rows = data[
         data["prognosis"] == predicted_disease
    ]

    predicted_row = predicted_rows.iloc[0]

    explanation = []

    for symptom in yes_symptoms:
        explanation.append({
             "symptom": symptom,
             "status": "match" if predicted_row[symptom] == 1 else "not_match"
        })

    for symptom in no_symptoms:
        explanation.append({
            "symptom": symptom,
            "status": "match" if predicted_row[symptom] == 0 else "not_match"
        })

    match_percentage = round(
        best_match["score"],
        1
    )

    candidate_count = len(possible_diseases)

    asked_symptoms = yes_symptoms + no_symptoms

    next_question = get_best_question(
        filtered_data,
        asked_symptoms
    )

    total_answers = len(asked_symptoms)

    # Stop after enough symptoms
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

    # Continue asking questions
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

    # No more questions
    return {
        "status": "complete",
        "disease": predicted_disease,
        "match_percentage": match_percentage,
        "next_question": None,
        "candidate_count": candidate_count,
        "conditions": possible_conditions,
        "explanation": explanation
    }