document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.getElementById('new-chat-btn');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const errorBanner = document.getElementById('error-banner');
    const errorMessage = document.getElementById('error-message');
    const closeErrorBtn = document.getElementById('close-error-btn');

    let conversationHistory = [];

    // Auto-resize textarea
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Mobile sidebar toggle
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 &&
            sidebar.classList.contains('open') &&
            !sidebar.contains(e.target) &&
            !mobileMenuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });

    // Handle Enter key submit (Shift+Enter for newline)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim() !== '') {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // New Chat handler
    newChatBtn.addEventListener('click', () => {
        conversationHistory = [];
        hideError();
        chatBox.innerHTML = `
            <div class="message system-message">
                <div class="message-content">
                    <i class="fas fa-sparkles welcome-icon"></i>
                    <h3>New Conversation Started</h3>
                    <p>Ask me any question in English or Tamil!</p>
                </div>
            </div>
        `;
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('open');
        }
    });

    // Error banner toggle
    closeErrorBtn.addEventListener('click', hideError);

    function showError(msg) {
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    // Submit handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        hideError();
        addMessageToUI('user', text);
        conversationHistory.push({ role: 'user', content: text });

        userInput.value = '';
        userInput.style.height = 'auto';

        const typingId = showTypingIndicator();
        sendBtn.disabled = true;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: conversationHistory })
            });

            const data = await response.json();
            removeElement(typingId);

            if (response.ok) {
                addMessageToUI('ai', data.message, true);
                conversationHistory.push({ role: 'assistant', content: data.message });
            } else {
                showError(data.error || 'Failed to generate response.');
                addMessageToUI('system', `Error: ${data.error || 'Something went wrong.'}`);
            }
        } catch (err) {
            removeElement(typingId);
            showError('Network error. Check your server connection.');
            addMessageToUI('system', 'Network error: Unable to reach the server.');
            console.error(err);
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    function addMessageToUI(sender, text, isMarkdown = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (isMarkdown && typeof marked !== 'undefined') {
            contentDiv.innerHTML = marked.parse(text);
        } else {
            const p = document.createElement('p');
            p.textContent = text;
            contentDiv.appendChild(p);
        }

        messageDiv.appendChild(contentDiv);
        chatBox.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = id;
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        `;
        chatBox.appendChild(typingDiv);
        scrollToBottom();
        return id;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        chatBox.scrollTo({
            top: chatBox.scrollHeight,
            behavior: 'smooth'
        });
    }
});
