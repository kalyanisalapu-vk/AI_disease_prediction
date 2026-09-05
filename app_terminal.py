import pandas as pd
import joblib

# Load dataset
data = pd.read_csv("Training.csv")

# Remove unnecessary column
data = data.drop(columns=["Unnamed: 133"])

# Load saved model
model = joblib.load("disease_model.pkl")

# Load symptoms
all_symptoms = joblib.load("symptoms.pkl")

print("Disease Prediction System Started Successfully!")
print("Total Symptoms:", len(all_symptoms))

def get_next_symptoms(selected_symptoms, top_n=10):

    # Start with all data
    filtered_data = data.copy()

    # Keep only rows containing ALL selected symptoms
    for symptom in selected_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 1
        ]

    # If no matching rows, return empty list
    if filtered_data.empty:
        return []

    # Get remaining possible diseases
    possible_diseases = filtered_data["prognosis"].unique()

    # Keep data only for those possible diseases
    disease_data = data[
        data["prognosis"].isin(possible_diseases)
    ]

    # Get symptom frequencies
    symptom_counts = disease_data[all_symptoms].sum()

    # Remove already selected symptoms
    symptom_counts = symptom_counts.drop(
        selected_symptoms,
        errors="ignore"
    )

    # Remove symptoms that are not present
    symptom_counts = symptom_counts[symptom_counts > 0]

    # Return top related symptoms
    next_symptoms = (
        symptom_counts
        .sort_values(ascending=False)
        .head(top_n)
    )

    return next_symptoms


def get_possible_diseases(selected_symptoms):

    # Start with all data
    filtered_data = data.copy()

    # Keep only rows where all selected symptoms are present
    for symptom in selected_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 1
        ]

    # Get unique possible diseases
    possible_diseases = filtered_data["prognosis"].unique()

    return possible_diseases


# ==========================
# TESTING CODE
# ==========================

# ==========================
# AUTOMATIC YES / NO SYSTEM
# ==========================

yes_symptoms = []
no_symptoms = []

print("\n--- Disease Prediction System ---")

# ==========================
# FIRST SYMPTOM SEARCH
# ==========================

print("\nSelect your first symptom.")

while True:

    # User types a few letters
    search = input(
        "\nSearch your symptom (type a few letters): "
    ).strip().lower()

    # Convert spaces to underscores for searching
    search_clean = search.replace(" ", "_")

    # Find matching symptoms
    matches = [
        symptom for symptom in all_symptoms
        if search_clean in symptom
        or search in symptom.replace("_", " ")
    ]

    # No matches
    if len(matches) == 0:
        print("\nNo matching symptoms found. Try again.")
        continue

    # Show only matching symptoms
    print("\nMatching symptoms:")

    for i, symptom in enumerate(matches, start=1):
        print(
            f"{i}. {symptom.replace('_', ' ').title()}"
        )

    # Select one from matches
    while True:
        try:
            choice = int(
                input("\nSelect symptom number: ")
            )

            if 1 <= choice <= len(matches):
                first_symptom = matches[choice - 1]
                break
            else:
                print("Please enter a valid number.")

        except ValueError:
            print("Please enter a number.")

    break
yes_symptoms.append(first_symptom)

print("\nYou selected:", first_symptom.replace("_", " ").title())


# Filter diseases based on YES and NO answers
def filter_diseases(yes_symptoms, no_symptoms):

    filtered_data = data.copy()

    # Symptoms that user HAS
    for symptom in yes_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 1
        ]

    # Symptoms that user DOES NOT HAVE
    for symptom in no_symptoms:
        filtered_data = filtered_data[
            filtered_data[symptom] == 0
        ]

    return filtered_data


# Find the best next symptom to ask
def get_best_question(filtered_data, asked_symptoms):

    possible_diseases = filtered_data["prognosis"].unique()

    # If only one disease remains, stop asking
    if len(possible_diseases) <= 1:
        return None

    # Check only remaining symptom columns
    remaining_symptoms = [
        symptom for symptom in all_symptoms
        if symptom not in asked_symptoms
    ]

    best_symptom = None
    best_score = -1

    # Find symptom that best separates the remaining cases
    for symptom in remaining_symptoms:

        yes_count = (filtered_data[symptom] == 1).sum()
        no_count = (filtered_data[symptom] == 0).sum()

        # Skip symptoms that don't separate anything
        if yes_count == 0 or no_count == 0:
            continue

        # Balanced YES/NO split = better question
        score = min(yes_count, no_count)

        if score > best_score:
            best_score = score
            best_symptom = symptom

    return best_symptom


# ==========================
# AUTOMATIC QUESTION LOOP
# ==========================

while True:

    filtered_data = filter_diseases(
        yes_symptoms,
        no_symptoms
    )

    possible_diseases = filtered_data["prognosis"].unique()

    # Stop if no disease matches
    if len(possible_diseases) == 0:
        print("\nNo clear matching disease found.")
        break

    # Stop if one disease remains
    if len(possible_diseases) == 1:
        predicted_disease = possible_diseases[0]

        print("\n==============================")
        print("Analyzing your symptoms...")
        print("\nFinal Predicted Disease:")
        print(">>>", predicted_disease)
        print("==============================")

        print("\n⚠️ Important:")
        print("This result is only a preliminary prediction")
        print("based on the symptoms provided.")
        print("Please consult a qualified doctor or healthcare")
        print("professional for proper diagnosis and treatment.")

        break

    # Get the best symptom to ask next
    asked_symptoms = yes_symptoms + no_symptoms

    next_symptom = get_best_question(
        filtered_data,
        asked_symptoms
    )

    # No useful question available
    if next_symptom is None:
        print("\nMore information is needed for prediction.")
        break

    # Ask user YES / NO question
    while True:

        answer = input(
            f"\nDo you have "
            f"{next_symptom.replace('_', ' ').title()}? "
            f"(yes/no): "
        ).strip().lower()

        if answer in ["yes", "y"]:
            yes_symptoms.append(next_symptom)
            break

        elif answer in ["no", "n"]:
            no_symptoms.append(next_symptom)
            break

        else:
            print("Please answer only yes or no.")