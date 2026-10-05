import os
import re
import math
import logging
from datetime import datetime
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Offline local AI response generator with Dynamic Time/Date support
class OfflineAIModel:
    def __init__(self):
        self.pipeline = None
        self._init_local_model()

    def _init_local_model(self):
        """Attempts to load a lightweight local HuggingFace model if available, with offline fallback."""
        try:
            from transformers import pipeline
            app.logger.info("Initializing local HuggingFace Transformers pipeline...")
            self.pipeline = pipeline("text2text-generation", model="google/flan-t5-small", max_length=256)
            app.logger.info("Local Transformers model loaded successfully.")
        except Exception as e:
            app.logger.warning(f"Local Transformers pipeline load skipped/failed ({e}). Using built-in local AI knowledge engine.")
            self.pipeline = None

    def _get_ist_datetime(self):
        try:
            tz = zoneinfo.ZoneInfo("Asia/Kolkata")
            return datetime.now(tz)
        except Exception:
            return datetime.now()

    def generate_response(self, prompt, history):
        prompt_clean = prompt.strip().lower()
        now = self._get_ist_datetime()

        # 1. Dynamic Current Time Handling (English & Tamil)
        time_keywords = [
            "what time is it", "what is the current time", "time now", "current time",
            "what's the time", "tell me the time", "clock now",
            "இப்போ மணி என்ன", "இப்போது என்ன நேரம்", "மணி என்ன", "நேரம் என்ன"
        ]
        if any(kw in prompt_clean for kw in time_keywords):
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%B %d, %Y")
            if any(c in prompt for c in ['மணி', 'நேரம்', 'இப்போ']):
                return f"இந்தியாவில் தற்போதைய நேரம் **{time_str}** (IST), நாள்: **{date_str}**."
            return f"The current time in India is **{time_str}** (IST) on **{date_str}**."

        # 2. Dynamic Current Date / Day Handling (English & Tamil)
        date_keywords = [
            "today's date", "what is today's date", "what date is today", "current date",
            "what day is today", "day today", "today date",
            "இன்று என்ன தேதி", "இன்று என்ன கிழமை", "இன்றைய தேதி"
        ]
        if any(kw in prompt_clean for kw in date_keywords):
            day_str = now.strftime("%A")
            date_str = now.strftime("%B %d, %Y")
            if any(c in prompt for c in ['தேதி', 'கிழமை', 'இன்று']):
                return f"இன்றைய தேதி **{date_str}** ({day_str})."
            return f"Today's date is **{date_str}** ({day_str})."

        # 3. Math evaluation (e.g., "what is 25 * 4", "evaluate 100 / 5", "calculate 12 + 15")
        math_match = re.search(r'(?:what is|calculate|evaluate|how much is)?\s*([\d\.\s\+\-\*\/\^\(\)]+)', prompt_clean)
        if math_match and any(op in prompt_clean for op in ['+', '-', '*', '/', '^']):
            expr = math_match.group(1).replace('^', '**').strip()
            try:
                if re.match(r'^[0-9\.\s\+\-\*\/\(\)]+$', expr):
                    result = eval(expr)
                    return f"The result of **{expr}** is **{result}**."
            except Exception:
                pass

        # 4. General Knowledge & Definitions offline lookup
        kb = {
            "capital of india": "The capital of India is **New Delhi**.",
            "capital of france": "The capital of France is **Paris**.",
            "capital of usa": "The capital of the United States is **Washington, D.C.**",
            "capital of japan": "The capital of Japan is **Tokyo**.",
            "capital of tamil nadu": "The capital of Tamil Nadu is **Chennai**.",
            "who created python": "Python was created by **Guido van Rossum** and first released in 1991.",
            "what is python": "Python is a high-level, interpreted, general-purpose programming language known for its clear syntax and readability.",
            "what is html": "HTML (HyperText Markup Language) is the standard markup language used to create structured web pages.",
            "what is css": "CSS (Cascading Style Sheets) is a stylesheet language used to describe the presentation and layout of HTML documents.",
            "what is javascript": "JavaScript is a lightweight, interpreted programming language widely used to create dynamic and interactive content on the web.",
            "what is flask": "Flask is a lightweight WSGI web application framework written in Python designed to make getting started quick and easy.",
            "what is ai": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines programmed to think, learn, and solve problems.",
            "what is photosynthesis": "Photosynthesis is the process by which green plants and some organisms use sunlight to synthesize nutrients from carbon dioxide and water.",
            "vanakkam": "வணக்கம்! நான் NovaChat AI. உங்களுக்கு இன்று எவ்வாறு உதவ முடியும்?",
            "eppadi irukkinga": "நான் நலமாக இருக்கிறேன்! உங்களுக்கு என்ன கேள்வி அல்லது உதவி தேவை?",
            "hi": "Hello! I am NovaChat AI, your offline AI assistant. How can I help you today?",
            "hello": "Hello! I am NovaChat AI. Feel free to ask any question in English or Tamil.",
            "who are you": "I am NovaChat AI, a helpful general-purpose AI assistant running completely local and offline without any external API keys.",
            "how are you": "I am functioning great! How can I assist you with your questions today?"
        }

        for key, answer in kb.items():
            if key in prompt_clean:
                return answer

        # 5. Use local HuggingFace Transformers pipeline if loaded
        if self.pipeline:
            try:
                res = self.pipeline(f"Answer clearly: {prompt}")
                if res and len(res) > 0 and 'generated_text' in res[0]:
                    text = res[0]['generated_text'].strip()
                    if text:
                        return text
            except Exception as ex:
                app.logger.error(f"Transformers pipeline generation error: {ex}")

        # 6. Fallback smart contextual local answer generator
        if "tamil" in prompt_clean or any(c in prompt for c in ['ந', 'ல', 'ம', 'க', 'வ']):
            return f"உங்கள் கேள்வி: '{prompt}'. NovaChat AI உள்ளூர் கணினி வழியில் பதிலளிக்கிறது. மேலும் விவரங்களை கேட்கலாம்!"
        
        return f"**NovaChat AI (Offline Response):**\n\nRegarding **\"{prompt}\"**:\nThis is a general inquiry. NovaChat AI is running completely offline locally without external cloud dependencies. You can ask me mathematics, programming definitions, general knowledge, or Tamil questions!"

# Instantiate local model
local_ai = OfflineAIModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'messages' not in data:
        return jsonify({'error': 'No messages provided in request.'}), 400

    messages = data.get('messages', [])
    if not messages:
        return jsonify({'error': 'Message history is empty.'}), 400

    latest_message = messages[-1].get('content', '')

    try:
        response_text = local_ai.generate_response(latest_message, messages)
        return jsonify({'message': response_text})
    except Exception as e:
        app.logger.error(f"Offline AI error: {str(e)}")
        return jsonify({'error': f"Failed to generate response: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
