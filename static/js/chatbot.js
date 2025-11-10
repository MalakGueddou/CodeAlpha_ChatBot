class StudyBuddyChatbot {
    constructor() {
        this.isProcessing = false;
        this.conversationHistory = [];
        this.initialized = false; // 🔥 Nouveau : flag d'initialisation
        
        this.initializeEventListeners();
        this.showWelcomeMessage();
    }

    initializeEventListeners() {
        // 🔥 Empêcher la double initialisation
        if (this.initialized) {
            console.log('⚠️ Déjà initialisé');
            return;
        }
        
        console.log('🚀 Initialisation des événements...');

        // Bouton d'envoi - UN SEUL écouteur
        const sendBtn = document.getElementById('sendButton');
        if (sendBtn && !sendBtn.hasListener) {
            sendBtn.addEventListener('click', () => this.sendMessage());
            sendBtn.hasListener = true;
        }

        // Input utilisateur - UN SEUL écouteur
        const userInput = document.getElementById('userInput');
        if (userInput && !userInput.hasListener) {
            userInput.addEventListener('input', () => this.toggleSendButton());
            userInput.hasListener = true;
            userInput.focus();
        }

        // Actions rapides - UN SEUL écouteur par bouton
        const actionButtons = document.querySelectorAll('.action-btn');
        actionButtons.forEach(btn => {
            if (!btn.hasListener) {
                btn.addEventListener('click', (e) => {
                    const action = e.target.getAttribute('data-action') || 
                                 e.target.closest('.action-btn').getAttribute('data-action');
                    this.handleQuickAction(action);
                });
                btn.hasListener = true;
            }
        });

        // Boutons d'emoji - UN SEUL écouteur par bouton
        const emojiButtons = document.querySelectorAll('.action-icon');
        emojiButtons.forEach((btn, index) => {
            if (!btn.hasListener) {
                btn.addEventListener('click', () => {
                    const emojis = ['😊', '📚', '🎯'];
                    this.addEmoji(emojis[index] || '😊');
                });
                btn.hasListener = true;
            }
        });

        // Boutons header - UN SEUL écouteur par bouton
        const clearBtn = document.getElementById('clearChatBtn');
        if (clearBtn && !clearBtn.hasListener) {
            clearBtn.addEventListener('click', () => this.clearChat());
            clearBtn.hasListener = true;
        }

        const exportBtn = document.getElementById('exportChatBtn');
        if (exportBtn && !exportBtn.hasListener) {
            exportBtn.addEventListener('click', () => this.exportChat());
            exportBtn.hasListener = true;
        }

        this.initialized = true; // 🔥 Marquer comme initialisé
        console.log('✅ Tous les événements initialisés (sans duplication)');
    }

    handleQuickAction(action) {
        console.log('🔘 Action rapide:', action);
        
        const actions = {
            'notes': 'Je veux apprendre à prendre de bonnes notes efficaces',
            'planning': 'Aide-moi à créer un planning d étude personnalisé',
            'revision': 'Comment bien réviser pour mes examens ? Donne-moi une stratégie',
            'stress': 'Je stress beaucoup pour mon examen, aide-moi à gérer ce stress',
            'memoire': 'Comment améliorer ma mémoire pour mieux retenir mes cours ?'
        };

        const message = actions[action];
        if (message) {
            const userInput = document.getElementById('userInput');
            if (userInput) {
                userInput.value = message;
                this.sendMessage();
            }
        }
    }

    addEmoji(emoji) {
        const input = document.getElementById('userInput');
        if (input) {
            input.value += emoji;
            input.focus();
            this.toggleSendButton();
        }
    }

    showWelcomeMessage() {
        // Vérifier si le message de bienvenue existe déjà
        const existingWelcome = document.querySelector('.welcome-message');
        if (existingWelcome) return;

        setTimeout(() => {
            const welcomeDiv = document.createElement('div');
            welcomeDiv.className = 'message bot-message welcome-message';
            
            welcomeDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-header">
                        <span class="sender-name">StudyBuddy</span>
                        <span class="message-time">${new Date().toLocaleTimeString('fr-FR', { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                        })}</span>
                    </div>
                    <div class="message-text">
                        <p>👋 <strong>Salut ! Je suis StudyBuddy, ton meilleur pote d'étude !</strong></p>
                        <p>Je suis tellement content de faire ta connaissance ! 😊</p>
                        <p>Je peux t'aider avec :</p>
                        <ul>
                            <li>🎯 <strong>Planification intelligente</strong> - Des plannings sur mesure</li>
                            <li>📝 <strong>Techniques de prise de notes</strong> - Méthodes efficaces</li>
                            <li>🧠 <strong>Stratégies de mémorisation</strong> - Mémoire optimisée</li>
                            <li>⚡ <strong>Gestion du temps</strong> - Productivité maximale</li>
                            <li>😌 <strong>Gestion du stress</strong> - Bien-être garanti</li>
                        </ul>
                        <p><em>Parle-moi naturellement de tout ce qui concerne tes études ! Je suis là pour toi comme un vrai ami ! ✨</em></p>
                    </div>
                </div>
            `;
            
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.appendChild(welcomeDiv);
                this.scrollToBottom();
            }
        }, 500);
    }

    toggleSendButton() {
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendButton');
        if (userInput && sendBtn) {
            const hasText = userInput.value.trim().length > 0;
            sendBtn.disabled = !hasText;
            sendBtn.style.opacity = hasText ? '1' : '0.5';
            sendBtn.style.cursor = hasText ? 'pointer' : 'not-allowed';
        }
    }

    async sendMessage() {
        // 🔥 Empêcher l'envoi multiple
        if (this.isProcessing) {
            console.log('⚠️ Envoi déjà en cours...');
            return;
        }

        const userInput = document.getElementById('userInput');
        const message = userInput.value.trim();
        
        if (message === '') {
            return;
        }
        
        console.log('📤 Envoi du message:', message);
        
        // Ajouter le message utilisateur
        this.addMessage(message, 'user');
        userInput.value = '';
        this.toggleSendButton();
        
        this.isProcessing = true;
        
        try {
            // Afficher le message de réflexion
            const thinkingMessage = await this.showThinkingMessage();
            
            // Traitement avec l'IA
            const response = await this.processWithAI(message);
            
            // Supprimer le message de réflexion
            this.removeThinkingMessage(thinkingMessage);
            
            // Afficher la réponse avec effet de frappe
            await this.typeMessage(response.response, 'bot');
            
        } catch (error) {
            console.error('❌ Erreur:', error);
            this.removeThinkingMessage();
            this.addMessage(
                "Oups ! 🤖 J'ai rencontré un petit problème... Mais ne t'inquiète pas, je suis toujours là pour toi ! Peux-tu répéter ta question ?", 
                'bot'
            );
        } finally {
            this.isProcessing = false;
        }
    }

    async showThinkingMessage() {
        // Vérifier si un message de réflexion existe déjà
        const existingThinking = document.getElementById('thinkingMessage');
        if (existingThinking) {
            return existingThinking;
        }

        const chatMessages = document.getElementById('chatMessages');
        const thinkingDiv = document.createElement('div');
        thinkingDiv.className = 'message bot-message thinking-message';
        thinkingDiv.id = 'thinkingMessage';
        
        const thinkingMessages = [
            "Je réfléchis à la meilleure façon de t'aider... 💭",
            "Laisse-moi analyser ta question pour te donner la réponse parfaite... 🔍",
            "Je consulte mes connaissances pédagogiques pour toi... 📚",
            "Je cherche la méthode la plus adaptée à ta situation... 🎯",
            "Je prépare une réponse personnalisée rien que pour toi... ✨"
        ];
        
        const thinkingMessage = thinkingMessages[Math.floor(Math.random() * thinkingMessages.length)];
        
        thinkingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">StudyBuddy</span>
                    <span class="message-time">${new Date().toLocaleTimeString('fr-FR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    })}</span>
                </div>
                <div class="message-text thinking-text">
                    <em>${thinkingMessage}</em>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(thinkingDiv);
        this.scrollToBottom();
        
        return thinkingDiv;
    }

    removeThinkingMessage() {
        const thinkingMsg = document.getElementById('thinkingMessage');
        if (thinkingMsg) {
            thinkingMsg.remove();
        }
    }

    async processWithAI(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error('Erreur réseau: ' + response.status);
            }
            
            return await response.json();
        } catch (error) {
            console.error('❌ Erreur API:', error);
            throw error;
        }
    }

    // Dans la méthode typeMessage, améliorer l'affichage
    async typeMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Nettoyer le texte pour un meilleur affichage
    const cleanText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                         .replace(/\n/g, '<br>')
                         .replace(/•/g, '✨')
                         .replace(/✅/g, '✅')
                         .replace(/🎯/g, '🎯');
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender-name">${sender === 'user' ? 'Vous' : 'StudyBuddy'}</span>
                <span class="message-time">${new Date().toLocaleTimeString('fr-FR', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                })}</span>
            </div>
            <div class="message-text" id="typingMessage">${cleanText}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // Effet de frappe
    const messageText = document.getElementById('typingMessage');
    let currentText = '';
    let index = 0;
    const speed = 8; // Plus rapide pour une meilleure expérience
    
    await new Promise(resolve => {
        const typeWriter = () => {
            if (index < cleanText.length) {
                currentText += cleanText[index];
                messageText.innerHTML = currentText;
                index++;
                this.scrollToBottom();
                setTimeout(typeWriter, speed);
            } else {
                messageText.removeAttribute('id');
                resolve();
            }
        };
        typeWriter();
    });
    
    this.scrollToBottom();
    this.saveToHistory(text, sender);}

    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">${sender === 'user' ? 'Vous' : 'StudyBuddy'}</span>
                    <span class="message-time">${new Date().toLocaleTimeString('fr-FR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    })}</span>
                </div>
                <div class="message-text">${content}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        this.saveToHistory(content, sender);
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        }
    }

    saveToHistory(content, sender) {
        this.conversationHistory.push({
            content,
            sender,
            timestamp: new Date().toISOString()
        });
        
        if (this.conversationHistory.length > 50) {
            this.conversationHistory.shift();
        }
    }

    clearChat() {
        if (confirm('Voulez-vous vraiment effacer toute la conversation ?')) {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.innerHTML = '';
                this.conversationHistory = [];
                this.showWelcomeMessage();
            }
        }
    }

    exportChat() {
        if (this.conversationHistory.length === 0) {
            alert('Aucune conversation à exporter !');
            return;
        }

        const chatContent = this.conversationHistory.map(msg => 
            `${msg.sender === 'user' ? 'Vous' : 'StudyBuddy'} (${new Date(msg.timestamp).toLocaleString()}): ${msg.content.replace(/<[^>]*>/g, '')}`
        ).join('\n\n');
        
        const blob = new Blob([chatContent], { type: 'text/plain; charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `studybuddy-chat-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// 🔥 INITIALISATION UNIQUE - Version corrigée
let chatbotInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!chatbotInstance) {
        console.log('🚀 Création de StudyBuddy Chatbot...');
        chatbotInstance = new StudyBuddyChatbot();
        window.chatbot = chatbotInstance;
    } else {
        console.log('⚠️ StudyBuddy est déjà initialisé');
    }
});

// 🔥 Gestionnaire d'événements global UNIQUE
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (window.chatbot) {
            window.chatbot.sendMessage();
        }
    }
}