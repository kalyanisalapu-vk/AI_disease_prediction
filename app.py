from flask import Flask, request, jsonify, render_template
from prediction_logic import search_symptoms, get_prediction

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")

    matches = search_symptoms(query)

    return jsonify({
        "symptoms": matches
    })


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()

    first_symptom = data.get("symptom")

    if not first_symptom:
        return jsonify({
            "error": "Please select a symptom."
        }), 400

    yes_symptoms = [first_symptom]
    no_symptoms = []

    result = get_prediction(
        yes_symptoms,
        no_symptoms
    )
    print("SERVER RESULT:", result)

    return jsonify({
        "yes_symptoms": yes_symptoms,
        "no_symptoms": no_symptoms,
        **result
    })


@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()

    yes_symptoms = data.get("yes_symptoms", [])
    no_symptoms = data.get("no_symptoms", [])
    symptom = data.get("symptom")
    answer_value = data.get("answer")

    if not symptom or answer_value not in ["yes", "no"]:
        return jsonify({
            "error": "Invalid answer."
        }), 400

    if answer_value == "yes":
        yes_symptoms.append(symptom)
    else:
        no_symptoms.append(symptom)

    result = get_prediction(
        yes_symptoms,
        no_symptoms
    )

    return jsonify({
        "yes_symptoms": yes_symptoms,
        "no_symptoms": no_symptoms,
        **result
    })


if __name__ == "__main__":
    app.run(debug=False)