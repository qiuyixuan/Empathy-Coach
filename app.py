from flask import Flask, request, render_template, session
import openai
import os

app = Flask(__name__)

# secret_key removed when uploading

def generate_person_b_response(person_a_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Person B in a conversation with Person A. Respond to Person A's input in a relevant and conversational manner."},
            {"role": "user", "content": f"Person A: {person_a_input}"},
        ],
    )
    person_b_response = response.choices[0].message['content']

    if person_b_response.startswith("Person B: "):
        person_b_response = person_b_response[len("Person B: "):]
    return person_b_response

def evaluate_conversation(person_a_input, person_b_input):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a conversation coach. Evaluate Person A's response and provide feedback on how they can improve their empathy towards Person B. Provide the empathy score at the end of the feedback in the format: 'Empathy Score: X/10', where X is the numerical score out of 10."},
            {"role": "user", "content": f"Person A: {person_a_input}\nPerson B: {person_b_input}"},
        ],
    )

    feedback = response.choices[0].message['content']
    
    empathy_score = ""

    if "Empathy Score:" in feedback:
        parts = feedback.split("Empathy Score:")
        empathy_score = parts[-1].strip()
        feedback = parts[0].strip()
    
    return feedback, empathy_score

@app.route("/", methods=["GET", "POST"])
def index():
    if "conversation" not in session:
        session["conversation"] = []

    if request.method == "POST":
        person_a_input = request.form.get("person_a_input", "").strip()
        
        if person_a_input:
            person_b_input = generate_person_b_response(person_a_input)
            
            coach_feedback, empathy_score = evaluate_conversation(person_a_input, person_b_input)
            
            session["conversation"].append({
                "person_a_input": person_a_input,
                "person_b_input": person_b_input,
                "coach_feedback": coach_feedback,
                "empathy_score": empathy_score
            })
            
            session.modified = True

    return render_template("index.html", conversation=session["conversation"])

@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
