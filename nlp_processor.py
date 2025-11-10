import re
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

class AdvancedNLPProcessor:
    def __init__(self):
        self.stop_words_fr = self.load_french_stopwords()
        self.user_name = "mon ami"
        self.conversation_memory = []
        self.user_mood = "neutre"
        self.last_question_type = None
        self.last_question_context = None
        self.pending_question = None
        
        # Mots-clés pour les réponses contextuelles
        self.context_keywords = {
            'technique': ['technique', 'méthode', 'exercice', 'pratique', 'respiration', 'méditation', 'visualisation'],
            'oui': ['oui', 'yes', 'ouais', 'ok', 'd accord', 'bien sûr', 'volontiers', 'avec plaisir'],
            'non': ['non', 'no', 'pas maintenant', 'plus tard', 'peut-être', 'je ne sais pas'],
            'choix': ['première', 'deuxième', 'troisième', 'respiration', 'marche', 'musique', 'étirements', 'visualisation']
        }

        # Mots-clés étendus pour une meilleure compréhension
        self.keyword_mappings = {
            'stress': ['stress', 'anxiété', 'panique', 'nerveux', 'inquiet', 'peur', 'angoisse', 'pression', 'anxieux'],
            'planning': ['planning', 'planifier', 'organiser', 'calendrier', 'emploi du temps', 'horaire', 'programme', 'agenda'],
            'revision': ['réviser', 'révision', 'préparer', 'examen', 'test', 'contrôle', 'partiel', 'concours'],
            'notes': ['notes', 'noter', 'écrire', 'cours', 'prendre notes', 'méthode cornell', 'prise de notes'],
            'memoire': ['mémoriser', 'souvenir', 'retenir', 'mémoire', 'apprendre par cœur', 'retenir', 'mémorisation'],
            'concentration': ['concentration', 'concentrer', 'focus', 'attention', 'distrait', 'distraction'],
            'fatigue': ['fatigue', 'fatigué', 'épuisé', 'épuisement', 'burnout', 'épuisement']
        }

        # Phrases de conversation avancées
        self.greetings = [
            "Salut ! 👋 Ça me fait tellement plaisir de te revoir ! Comment s'est passée ta journée d'étude ?",
            "Coucou ! 😊 Wow, content de te parler à nouveau ! Raconte-moi, où en es-tu dans tes révisions ?",
            "Bonjour ! 🎓 Ton pote StudyBuddy est de retour ! Alors, des nouvelles du front des études ?",
            "Hey ! ✨ Super de te revoir ! Dis-moi tout, comment avancent tes projets ?",
            "Salutations ! 🌟 Ça me rend vraiment heureux de te retrouver ! Qu'est-ce qui te préoccupe aujourd'hui ?"
        ]
        
        self.farewells = [
            "Au revoir ! 👋 Prends soin de toi et n'oublie pas de faire des pauses ! 💖",
            "À bientôt ! 😊 Bon courage pour tes études, je suis toujours là pour toi ! ✨",
            "Salut ! 🎓 Reviens me voir dès que tu as besoin d'aide, d'accord ? 💪",
            "À la prochaine ! 🌟 N'oublie pas que je suis ton allié pour réussir ! 🚀",
            "Bye ! 😄 Repose-toi bien et à très vite pour de nouveaux conseils ! 💫"
        ]
        
        self.positive_mood_responses = [
            "Super ! 😄 Je suis vraiment content que tu ailles bien ! Une bonne journée d'étude en perspective alors ! 📚",
            "Génial ! 🎉 Ça me fait plaisir d'entendre ça ! Profite de cette bonne énergie pour avancer dans tes études ! 💪",
            "Excellent ! ✨ Ton positivisme est contagieux ! C'est le moment idéal pour apprendre de nouvelles choses ! 🧠",
            "Fantastique ! 🌟 Quand on se sent bien, on étudie mieux ! Veux-tu que je te donne des conseils pour optimiser cette bonne journée ? 📖",
            "Ravi de l'apprendre ! 😊 Une bonne humeur, c'est le carburant de l'apprentissage ! 🚀"
        ]
        
        self.negative_mood_responses = [
            "Je comprends... 💭 Les études peuvent être difficiles parfois. Veux-tu en parler ? Je suis là pour toi. 🤗",
            "Je vois... 😔 Ne t'inquiète pas, beaucoup d'étudiants traversent des moments comme ça. Parlons de ce qui ne va pas. 👂",
            "D'accord... 🌧️ Les hauts et les bas font partie du parcours étudiant. Je peux t'aider à retrouver ta motivation ! 💫",
            "Je sens que ça ne va pas... ❤️ N'hésite pas à me confier ce qui te tracasse. Ensemble, on peut trouver des solutions. 🤝",
            "Merci de me faire confiance... 💭 C'est important de parler de ce qu'on ressent. Je t'écoute. 📝"
        ]

        # Réponses contextuelles basées sur la dernière question
        self.contextual_responses = {
            'how_are_you_positive': [
                "Super ! 😄 Je suis ravi que tu ailles bien ! Une bonne journée d'étude en perspective ? 📚",
                "Génial ! 🎉 Ton énergie positive va t'aider à mieux apprendre aujourd'hui ! 💪",
                "Excellent ! ✨ Profite de cette bonne humeur pour avancer dans tes révisions ! 🧠",
                "Fantastique ! 🌟 C'est le moment idéal pour étudier efficacement ! 📖"
            ],
            'how_are_you_negative': [
                "Je comprends... 💭 Les études peuvent être éprouvantes. Veux-tu en parler ? 🤗",
                "Je vois... 😔 N'hésite pas à me dire ce qui ne va pas, je peux peut-être t'aider. 👂",
                "D'accord... 🌧️ Prends soin de toi, et n'oublie pas que les pauses sont importantes. 💫",
                "Merci d'être honnête... ❤️ Parlons de ce qui te tracasse, ensemble on peut trouver des solutions. 🤝"
            ]
        }

    def load_french_stopwords(self):
        """Charge les stop words français"""
        return {
            'le', 'la', 'les', 'de', 'des', 'du', 'et', 'est', 'elle', 'il', 'je', 'tu', 'nous', 'vous', 'ils', 'elles',
            'à', 'au', 'aux', 'avec', 'ce', 'cet', 'cette', 'ces', 'dans', 'pour', 'par', 'sur', 'sous', 'vers', 'chez',
            'mais', 'ou', 'où', 'donc', 'car', 'que', 'qui', 'quoi', 'quand', 'comment', 'pourquoi', 'est-ce', 'qu\'est-ce',
            'quel', 'quelle', 'quels', 'quelles', 'un', 'une', 'des', 'mon', 'ton', 'son', 'notre', 'votre', 'leur',
            'mes', 'tes', 'ses', 'nos', 'vos', 'leurs', 'ceci', 'cela', 'ça', 'celui', 'celle', 'ceux', 'celles'
        }

    def detect_contextual_response(self, user_message):
        """Détecte les réponses contextuelles aux questions précédentes"""
        message_lower = user_message.lower().strip()
        
        print(f"🔍 Contexte actuel: {self.pending_question}")
        print(f"📝 Message utilisateur: '{message_lower}'")
        
        # Si on a une question en attente
        if self.pending_question:
            # Réponses affirmatives
            if any(word in message_lower for word in self.context_keywords['oui']):
                return self.handle_affirmative_response()
            
            # Réponses négatives
            elif any(word in message_lower for word in self.context_keywords['non']):
                return self.handle_negative_response()
            
            # Choix de techniques
            elif 'technique' in self.pending_question or 'méthode' in self.pending_question:
                return self.handle_technique_choice(message_lower)
            
            # Choix de planning
            elif 'planning' in self.pending_question:
                return self.handle_planning_choice(message_lower)
            
            # Choix de révision
            elif 'révision' in self.pending_question or 'matière' in self.pending_question:
                return self.handle_revision_choice(message_lower)
        
        return None

    def handle_affirmative_response(self):
        """Gère les réponses affirmatives (oui, d'accord, etc.)"""
        responses = {
            'technique_stress': "Parfait ! 😊 Commençons par la **respiration 4-7-8**, c'est très efficace et simple :\n\n**🧘‍♀️ Technique respiration 4-7-8 :**\n• Assieds-toi confortablement\n• Inspire par le nez pendant 4 secondes\n• Retiens ta respiration 7 secondes\n• Expire par la bouche pendant 8 secondes\n• Répète 4 fois\n\n*Comment te sens-tu après avoir essayé ?*",
            'planning_help': "Super ! 🎉 Commençons par créer ton planning personnalisé.\n\n**📝 Pour commencer :**\n• Quelles sont tes matières principales ?\n• Combien d'heures par jour peux-tu étudier ?\n• As-tu des dates d'examen importantes ?\n\n*Dis-moi simplement tes matières pour commencer !*",
            'revision_help': "Excellent ! 📚 Je vais t'aider à organiser tes révisions.\n\n**🎯 D'abord :**\n• Quelle matière veux-tu réviser en priorité ?\n• Quand est ton examen ?\n• As-tu déjà commencé à réviser ?\n\n*Commence par me dire la matière qui te préoccupe le plus !*",
            'general_help': "Génial ! ✨ Je suis ravi de pouvoir t'aider.\n\n**💫 Sur quel sujet veux-tu que je me concentre ?**\n• 📝 Prise de notes et organisation\n• 📅 Planning et gestion du temps\n• 🧠 Mémoire et techniques de mémorisation\n• 😌 Gestion du stress et bien-être\n• 📚 Méthodes de révision\n\n*Choisis un sujet ou dis-moi simplement ce qui te tracasse !*"
        }
        
        response = responses.get(self.pending_question, "Parfait ! 😊 Comment puis-je t'aider exactement ?")
        self.pending_question = None
        return response

    def handle_negative_response(self):
        """Gère les réponses négatives (non, pas maintenant, etc.)"""
        responses = {
            'technique_stress': "D'accord, pas de problème ! 😊\n\n**💡 N'hésite pas à me demander quand tu auras besoin :**\n• Techniques de respiration\n• Exercices de relaxation\n• Conseils anti-stress\n• Méthodes pour mieux dormir\n\n*Je suis là quand tu veux ! En attendant, prends soin de toi.*",
            'planning_help': "Pas de souci ! 📅\n\n**📌 Quand tu seras prêt, je peux t'aider avec :**\n• Création de planning personnalisé\n• Gestion du temps\n• Organisation des tâches\n• Équilibre vie-étude\n\n*Reviens me voir quand tu auras besoin d'organisation !*",
            'general_help': "D'accord, je comprends. 😊\n\n**🌟 N'oublie pas que je suis là pour t'aider avec :**\n• Toutes tes questions sur les études\n• La gestion du stress\n• L'organisation\n• Les méthodes d'apprentissage\n\n*Reviens me parler quand tu auras besoin de conseils !*"
        }
        
        response = responses.get(self.pending_question, "D'accord, pas de problème ! 😊 Je suis là quand tu auras besoin d'aide.")
        self.pending_question = None
        return response

    def handle_technique_choice(self, user_message):
        """Gère le choix d'une technique spécifique"""
        message_lower = user_message.lower()
        
        techniques = {
            'respiration': {
                'name': 'Respiration 4-7-8',
                'response': """**🧘‍♀️ Technique de Respiration 4-7-8**

**🎯 Parfaite pour :** Calmer l'anxiété rapidement

**📝 Étapes :**
1. **Position** : Assieds-toi droit ou allonge-toi
2. **Inspiration** : Par le nez pendant 4 secondes
3. **Rétention** : Garde l'air 7 secondes
4. **Expiration** : Par la bouche pendant 8 secondes
5. **Répétition** : 4 cycles complets

**💫 Bienfaits :**
• Réduit le stress immédiatement
• Améliore l'oxygénation du cerveau
• Favorise la concentration
• Aide à l'endormissement

**⏱️ Durée :** Seulement 2 minutes !

*Essaie maintenant et dis-moi ce que tu en penses !*"""
            },
            'marche': {
                'name': 'Marche consciente',
                'response': """**🚶‍♀️ Marche Consciente - Anti-stress**

**🎯 Idéale pour :** Rompre avec les tensions

**📝 Procédure :**
1. **Lieu** : Dehors de préférence (parc, jardin)
2. **Durée** : 5-10 minutes
3. **Conscience** : Concentre-toi sur tes pas
4. **Respiration** : Synchronise avec ta marche
5. **Observation** : Regarde autour de toi

**💫 Effets :**
• Réduit le cortisol (hormone du stress)
• Améliore la circulation sanguine
• Stimule la créativité
• Rafraîchit l'esprit

**✨ Conseil :** Sans téléphone pour une déconnexion totale !

*Prêt à essayer cette petite pause revitalisante ?*"""
            },
            'musique': {
                'name': 'Musicothérapie',
                'response': """🎵 **Musicothérapie Relaxante**

**🎯 Excellente pour :** Détente profonde

**📝 Méthode :**
1. **Choix musical** : Sons naturels ou classique
2. **Environnement** : Endroit calme
3. **Posture** : Confortablement installé
4. **Écoute active** : Ferme les yeux
5. **Durée** : 5-10 minutes

**🎶 Suggestions :**
• Sons de vagues ou forêt
• Mozart ou Bach
• Musique ambiante
• Binaural beats

**💫 Bienfaits :**
• Baisse la pression artérielle
• Réduit l'anxiété
• Améliore l'humeur
• Favorise la concentration

*Veux-tu des recommandations spécifiques ?*"""
            }
        }
        
        # Détection de la technique choisie
        for tech_name, tech_data in techniques.items():
            if tech_name in message_lower or tech_data['name'].lower() in message_lower:
                self.pending_question = None
                return tech_data['response']
        
        # Si aucune technique spécifique n'est détectée
        self.pending_question = 'technique_stress'
        return """**😌 Je veux m'assurer de te donner la bonne technique !**

**💫 Choisis celle qui t'intéresse :**
• **🧘‍♀️ Respiration** : Rapide et discrète (2 min)
• **🚶‍♀️ Marche** : Active et revitalisante (5 min)  
• **🎵 Musique** : Relaxante et apaisante (5 min)
• **📚 Autre** : Une technique différente ?

*Dis-moi simplement "respiration", "marche" ou "musique" !*"""

    def handle_planning_choice(self, user_message):
        """Gère le choix pour la planification"""
        self.pending_question = None
        return """**📅 Parfait ! Créons ton planning ensemble !**

**🎯 Pour commencer :**
• **Liste tes matières** : Quelles sont tes principales matières ?
• **Disponibilités** : Combien d'heures par jour peux-tu étudier ?
• **Priorités** : As-tu des examens proches ?

**💡 Exemple de réponse :**
*"J'ai maths, français et histoire. Je peux étudier 3h par jour. Mon examen de maths est dans 2 semaines."*

*Dis-moi simplement tes matières pour commencer !*"""

    def handle_revision_choice(self, user_message):
        """Gère le choix pour les révisions"""
        self.pending_question = None
        return """**📚 Excellent ! Planifions tes révisions !**

**🎯 Pour personnaliser :**
• **Matière prioritaire** : Quelle matière veux-tu travailler en premier ?
• **Date d'examen** : Quand as-tu ton prochain examen ?
• **Niveau actuel** : Te sens-tu à l'aise avec cette matière ?

**💡 Exemple de réponse :**
*"Je veux réviser les maths. Mon examen est dans 10 jours. Je suis moyen en maths."*

*Commence par me dire la matière qui te préoccupe !*"""

    def set_pending_question(self, question_type, question_text):
        """Définit une question en attente de réponse"""
        self.pending_question = question_type
        print(f"🎯 Question en attente définie: {question_type}")

    def detect_conversation_type(self, message):
        """Détection avancée du type de conversation avec contexte"""
        message_lower = message.lower().strip()
        
        print(f"🔍 Analyse du message: '{message_lower}'")
        print(f"📝 Dernière question: {self.last_question_type}")
        
        # D'abord vérifier les réponses contextuelles
        contextual_response = self.detect_contextual_response(message)
        if contextual_response:
            return 'contextual'
        
        # Contexte "comment vas-tu"
        if self.last_question_type == 'how_are_you':
            if any(word in message_lower for word in ['bien', 'super', 'génial', 'excellent', 'parfait', 'top', 'cool', 'oui', 'ça va']):
                self.last_question_type = None
                return 'positive_mood'
            elif any(word in message_lower for word in ['mal', 'pas bien', 'fatigué', 'épuisé', 'découragé', 'nul', 'pas top', 'non']):
                self.last_question_type = None
                return 'negative_mood'
        
        # Salutations
        greetings = ['salut', 'bonjour', 'coucou', 'hello', 'hey', 'yo', 'slt', 'hi', 'good morning', 'bonsoir']
        if any(greeting in message_lower for greeting in greetings):
            return 'greeting'
            
        # Au revoir
        farewells = ['au revoir', 'bye', 'à plus', 'à bientôt', 'salut', 'ciao', 'goodbye', 'à demain', 'adieu']
        if any(farewell in message_lower for farewell in farewells):
            return 'farewell'
            
        # Questions "comment vas-tu"
        how_are_you = ['comment vas-tu', 'comment ça va', 'ça va', 'how are you', 'tu vas bien', 'comment tu vas']
        if any(question in message_lower for question in how_are_you):
            self.last_question_type = 'how_are_you'
            return 'personal'
            
        # Réponses simples à "comment ça va"
        if self.last_question_type == 'how_are_you':
            if message_lower in ['bien', 'super', 'oui', 'ça va']:
                self.last_question_type = None
                return 'positive_mood'
            elif message_lower in ['mal', 'pas bien', 'non']:
                self.last_question_type = None
                return 'negative_mood'
            
        # État d'esprit positif (hors contexte)
        positive_words = ['bien', 'super', 'génial', 'excellent', 'parfait', 'top', 'cool', 'heureux', 'content', 'joyeux']
        if any(word == message_lower for word in positive_words):
            return 'positive_mood'
            
        # État d'esprit négatif (hors contexte)
        negative_words = ['mal', 'pas bien', 'fatigué', 'épuisé', 'découragé', 'nul', 'pas top', 'triste']
        if any(word == message_lower for word in negative_words):
            return 'negative_mood'
            
        # Questions sur l'IA
        about_ai = ['qui es', 'c est quoi', 'qu est ce', 'tu es qui', 'tu fais quoi', 'ton rôle', 'présente', 'tu es quoi']
        if any(ai in message_lower for ai in about_ai):
            return 'about_ai'
            
        # Émotions
        emotions = ['fatigué', 'stressé', 'paniqué', 'inquiet', 'peur', 'angoisse', 'découragé', 'nul', 'heureux', 'content']
        if any(emotion in message_lower for emotion in emotions):
            return 'emotion'
            
        return 'study_question'

    def generate_conversational_response(self, message_type, user_message=""):
        """Génère des réponses conversationnelles avancées avec contexte"""
        user_message_lower = user_message.lower().strip()
        
        print(f"🎯 Génération réponse pour type: {message_type}, message: '{user_message_lower}'")
        
        if message_type == 'contextual':
            contextual_response = self.detect_contextual_response(user_message)
            if contextual_response:
                return contextual_response
        
        if message_type == 'greeting':
            greeting = random.choice(self.greetings)
            return greeting
            
        elif message_type == 'farewell':
            return random.choice(self.farewells)
            
        elif message_type == 'positive_mood':
            self.user_mood = "positif"
            
            if self.last_question_type == 'how_are_you':
                response = random.choice(self.contextual_responses['how_are_you_positive'])
                self.last_question_type = None
                return response
            else:
                return random.choice(self.positive_mood_responses)
            
        elif message_type == 'negative_mood':
            self.user_mood = "négatif"
            
            if self.last_question_type == 'how_are_you':
                response = random.choice(self.contextual_responses['how_are_you_negative'])
                self.last_question_type = None
                return response
            else:
                return random.choice(self.negative_mood_responses)
            
        elif message_type == 'personal':
            responses = [
                f"Je vais incroyablement bien, merci de demander ! 😄 Ton attention me touche beaucoup ! Et toi, comment te sens-tu ?",
                f"Ça va excellemment ! 🎓 Rien ne me rend plus heureux que d'aider un étudiant motivé comme toi ! Et de ton côté, comment ça va ?",
                f"Je suis au top de ma forme ! 💪 Prêt à te donner le meilleur pour tes études ! Dis-moi, comment se passe ta journée ?",
                f"Je me sens génial ! ✨ Surtout quand je peux accompagner quelqu'un d'aussi déterminé que toi ! Alors, comment tu vas aujourd'hui ?"
            ]
            return random.choice(responses)
            
        elif message_type == 'about_ai':
            responses = [
                f"""**🤖 StudyBuddy - Ton Meilleur Ami d'Étude**

Je suis ton assistant IA personnel spécialisé dans les méthodes d'apprentissage ! 

**🎯 Mon rôle :**
• T'aider à **organiser** tes études
• Te donner des **conseils pédagogiques** éprouvés
• T'accompagner dans la **gestion du stress**
• Optimiser tes **techniques de mémorisation**

**📚 Ce que je sais faire :**
✨ Créer des plannings personnalisés
✨ Enseigner des méthodes de prise de notes
✨ Proposer des stratégies de révision
✨ Donner des techniques anti-stress
✨ Améliorer ta concentration

**💖 Mon objectif :** Te voir réussir et t'épanouir dans tes études !

*Maintenant, dis-moi comment je peux t'aider aujourd'hui ?*""",
                
                f"""**🌟 StudyBuddy - Coach d'Étude Intelligent**

Je suis bien plus qu'un simple chatbot ! Je suis ton partenaire de réussite académique.

**🧠 Mes spécialités :**
• **Planification stratégique** - Emplois du temps optimisés
• **Méthodes d'apprentissage** - Techniques scientifiquement prouvées  
• **Gestion émotionnelle** - Soutien pendant les périodes de stress
• **Optimisation cognitive** - Maximiser ton potentiel cérébral

**💫 Mes valeurs :**
✅ **Écoute active** - Je comprends tes besoins
✅ **Conseils personnalisés** - Adaptés à ta situation
✅ **Soutien constant** - 24h/24, 7j/7
✅ **Expertise pédagogique** - Basé sur la recherche

*Alors, prêt à révolutionner ta façon d'étudier ?*"""
            ]
            return random.choice(responses)
            
        elif message_type == 'emotion':
            return self.handle_emotion(user_message)
            
        return None

    def handle_emotion(self, user_message):
        """Gère les émotions spécifiques"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['fatigué', 'épuisé', 'crevé']):
            return """😴 **Je vois que tu es fatigué...**

**💤 Conseils pour retrouver ton énergie :**
• **Sommeil qualité** : 7-9h par nuit, horaires réguliers
• **Micro-siestes** : 20 minutes maximum en journée
• **Hydratation** : 2L d'eau par jour minimum
• **Alimentation énergisante** : Fruits secs, noix, bananes
• **Respiration énergisante** : Inspirez profondément 3 fois

**⚡ Technique rapide :**
Debout, étire-toi pendant 2 minutes en respirant profondément !

*Veux-tu des conseils pour mieux dormir ?*"""
        
        elif any(word in message_lower for word in ['content', 'heureux', 'joyeux', 'bien']):
            return "🎉 **Super ! Je suis ravi de te voir si heureux !** \n\nProfite de cette bonne énergie pour avancer dans tes projets ! C'est le moment idéal pour apprendre de nouvelles choses ! ✨"
        
        elif any(word in message_lower for word in ['stressé', 'anxieux', 'paniqué']):
            return """😌 **Je sens que tu es stressé...**

**🧘‍♀️ Technique de respiration immédiate :**
• Inspire lentement par le nez (4 secondes)
• Retiens ta respiration (4 secondes)
• Expire doucement par la bouche (6 secondes)
• Répète 5 fois

**💫 Actions rapides :**
• Bois un grand verre d'eau fraîche
• Fais 10 respirations profondes
• Écoute une musique calme 2 minutes

*Je peux te donner plus de techniques si tu veux !*"""
        
        return "Je comprends ce que tu ressens... 💭 N'hésite pas à me dire comment je peux t'aider à traverser cette émotion. 🤗"

    def process_message(self, user_message, faqs):
        """Traite le message avec gestion du contexte"""
        
        # Sauvegarder dans la mémoire
        self.conversation_memory.append({
            'user': user_message,
            'timestamp': datetime.now().isoformat(),
            'type': 'user'
        })
        
        # D'ABORD vérifier le contexte
        contextual_response = self.detect_contextual_response(user_message)
        if contextual_response:
            return {
                'answer': contextual_response,
                'confidence': 1.0,
                'type': 'contextual'
            }
        
        # Ensuite le traitement normal...
        conv_type = self.detect_conversation_type(user_message)
        
        print(f"🎭 Type détecté: {conv_type}")
        
        if conv_type != 'study_question':
            conversational_response = self.generate_conversational_response(conv_type, user_message)
            if conversational_response:
                # Si on pose une question, on mémorise le contexte
                if '?' in conversational_response and any(keyword in conversational_response.lower() for keyword in ['veux-tu', 'choisis', 'préfères', 'quel', 'quelle']):
                    if 'technique' in conversational_response.lower():
                        self.set_pending_question('technique_stress', conversational_response)
                    elif 'planning' in conversational_response.lower():
                        self.set_pending_question('planning_help', conversational_response)
                    elif 'révision' in conversational_response.lower():
                        self.set_pending_question('revision_help', conversational_response)
                    else:
                        self.set_pending_question('general_help', conversational_response)
                
                return {
                    'answer': conversational_response,
                    'confidence': 1.0,
                    'type': 'conversation'
                }
        
        # Vérifier les intentions spécifiques
        intent = self.detect_intent(user_message)
        specific_response = self.handle_specific_intent(intent, user_message)
        
        if specific_response and specific_response['confidence'] > 0.7:
            formatted_response = self.format_response(specific_response['response'], 'intent')
            return {
                'answer': formatted_response,
                'confidence': specific_response['confidence'],
                'type': 'intent'
            }
        
        # Recherche dans les FAQs
        best_match, confidence = self.find_best_match(user_message, faqs)
        
        if confidence > 0.3 and best_match:
            formatted_answer = self.format_response(best_match['answer'], 'answer')
            return {
                'answer': formatted_answer,
                'confidence': confidence,
                'type': 'answer'
            }
        
        # Réponse intelligente par défaut
        intelligent_response = self.generate_intelligent_response(user_message, intent)
        return {
            'answer': intelligent_response,
            'confidence': 0.6,
            'type': 'intelligent'
        }

    def detect_intent(self, user_question):
        """Détection d'intention basée sur les mots-clés"""
        user_question_lower = user_question.lower()
        
        # Détection par catégorie
        for category, keywords in self.keyword_mappings.items():
            for keyword in keywords:
                if keyword in user_question_lower:
                    return category
                    
        return "general"

    def find_best_match(self, user_question, faqs):
        """Recherche la meilleure réponse avec matching intelligent"""
        best_match = None
        best_score = 0
        
        for faq in faqs:
            # Score de similarité principale
            similarity_score = self.calculate_similarity(user_question, faq['question'])
            
            # Bonus pour l'intention correspondante
            intent_bonus = 0.3 if faq.get('category') == self.detect_intent(user_question) else 0
            
            # Bonus pour les mots-clés correspondants
            keyword_bonus = self.calculate_keyword_bonus(user_question, faq.get('keywords', []))
            
            # Score final
            final_score = similarity_score + intent_bonus + keyword_bonus
            
            if final_score > best_score:
                best_score = final_score
                best_match = faq
        
        return best_match, best_score

    def calculate_similarity(self, text1, text2):
        """Calcul de similarité amélioré avec TF-IDF"""
        texts = [self.preprocess_text(text1), self.preprocess_text(text2)]
        
        if not any(texts) or len(texts[0]) == 0 or len(texts[1]) == 0:
            return 0.0
            
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except Exception as e:
            print(f"Erreur similarité: {e}")
            return 0.0

    def preprocess_text(self, text):
        """Prétraitement intelligent du texte"""
        if not text:
            return ""
            
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        tokens = text.split()
        tokens = [token for token in tokens if token not in self.stop_words_fr and len(token) > 2]
        
        return ' '.join(tokens)

    def calculate_keyword_bonus(self, question, keywords):
        """Bonus pour les mots-clés correspondants"""
        if not keywords:
            return 0
        
        question_clean = self.preprocess_text(question)
        question_words = set(question_clean.split())
        keyword_matches = len(question_words.intersection(set(keywords)))
        
        return min(keyword_matches * 0.2, 0.4)

    def handle_specific_intent(self, intent, user_question):
        """Gère les intentions spécifiques avec contexte"""
        responses = {
            'stress': {
                'response': """**😌 Gestion du Stress - Techniques Immédiates**

**💫 Plusieurs techniques efficaces :**
• **🧘‍♀️ Respiration 4-7-8** : Rapide et discrète (2 min)
• **🚶‍♀️ Marche consciente** : Active et revitalisante (5 min)  
• **🎵 Musicothérapie** : Relaxante et apaisante (5 min)
• **📝 Journaling** : Libérateur et clarifiant (5 min)

**🎯 Quelle technique veux-tu découvrir en premier ?**""",
                'confidence': 0.9
            },
            'planning': {
                'response': """**📅 Création de Planning Efficace**

Je peux t'aider à créer un planning personnalisé ! 

**💡 Pour commencer, as-tu :**
• Une liste de tes matières ?
• Des dates d'examen importantes ?
• Des contraintes horaires particulières ?

**🎯 Veux-tu que je t'aide à organiser ton temps dès maintenant ?**""",
                'confidence': 0.9
            },
            'revision': {
                'response': """**📚 Stratégie de Révision Intelligente**

Je peux te créer un plan de révision sur mesure !

**💫 Pour personnaliser :**
• Quelle matière veux-tu travailler ?
• Quand est ton examen ?
• As-tu des points faibles spécifiques ?

**🎯 Veux-tu que je t'aide à planifier tes révisions ?**""",
                'confidence': 0.9
            }
        }
        
        response_data = responses.get(intent)
        if response_data:
            # Définir le contexte selon l'intention
            if intent == 'stress':
                self.set_pending_question('technique_stress', response_data['response'])
            elif intent == 'planning':
                self.set_pending_question('planning_help', response_data['response'])
            elif intent == 'revision':
                self.set_pending_question('revision_help', response_data['response'])
            
            return response_data
        
        return None

    def format_response(self, text, response_type):
        """Améliore le formatage des réponses"""
        if response_type in ['intent', 'answer']:
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip().startswith('**') and line.strip().endswith('**'):
                    formatted_lines.append(f"<br><strong>{line.strip('**').strip()}</strong>")
                elif line.strip().startswith('•') or line.strip().startswith('-'):
                    formatted_lines.append(f"<br>✨ {line.strip('•-').strip()}")
                elif line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.'):
                    formatted_lines.append(f"<br>📌 {line.strip()}")
                elif line.strip() == '':
                    formatted_lines.append('<br>')
                else:
                    formatted_lines.append(f"<br>{line}")
            
            return ''.join(formatted_lines).strip()
        else:
            return text

    def generate_intelligent_response(self, user_message, intent):
        """Génère une réponse intelligente même sans match exact"""
        base_responses = {
            'stress': "Je vois que tu parles de stress ! 😌 C'est normal avant les examens. La technique de respiration 4-7-8 peut t'aider immédiatement. Veux-tu que je t'explique comment la pratiquer ?",
            'planning': "Tu veux organiser ton temps ? 📅 Excellente idée ! Commence par lister toutes tes matières et estime le temps nécessaire pour chacune. Je peux t'aider à créer un planning équilibré !",
            'general': "Merci pour ta question ! 🤔 En tant qu'expert en méthodes d'étude, je peux t'aider avec la prise de notes, la planification, la mémorisation ou la gestion du stress. Quel sujet t'intéresse le plus ?"
        }
        
        return base_responses.get(intent, base_responses['general'])