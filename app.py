from flask import Flask, render_template, request, jsonify
from nlp_processor import AdvancedNLPProcessor
import json
import os
from datetime import datetime

app = Flask(__name__)
nlp_processor = AdvancedNLPProcessor()

# Charger les FAQs
try:
    with open('static/data/faqs.json', 'r', encoding='utf-8') as f:
        faqs_data = json.load(f)
except Exception as e:
    print(f"Erreur chargement FAQs: {e}")
    faqs_data = {'faqs': []}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'response': "Hmm... je n'ai pas bien saisi votre message. Pouvez-vous reformuler ? 😊"
            })
        
        # Traitement NLP avancé avec réponses conversationnelles
        response = nlp_processor.process_message(user_message, faqs_data['faqs'])
        
        return jsonify({
            'success': True,
            'response': response['answer'],
            'confidence': response['confidence'],
            'type': response['type']
        })
        
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({
            'success': False,
            'response': "Oups ! J'ai rencontré un petit problème technique. Pouvez-vous réessayer ? 🤔",
            'type': 'error'
        })

@app.route('/api/suggestions')
def get_suggestions():
    suggestions = [
        "Comment optimiser ma prise de notes ? 📝",
        "Je stress pour mon examen, des conseils ? 😰",
        "Tu peux m'aider à créer un planning ? 📅",
        "J'ai du mal à me concentrer, aide-moi ! 🎯",
        "Des techniques pour mieux mémoriser ? 🧠"
    ]
    return jsonify(suggestions)

if __name__ == '__main__':
    print("🚀 StudyBuddy IA démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)