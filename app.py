import os
import json
from flask import Flask, render_template, request, Response, stream_with_context, jsonify, redirect, url_for
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq client securely from environment variables
groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
MODEL = 'llama-3.3-70b-versatile'

@app.route('/')
def index():
    """Serve the main frontend UI from the templates folder."""
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    """Serve the login page."""
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup():
    """Serve the signup page."""
    return render_template('signup.html')





@app.route('/api/chat', methods=['POST'])
def stream_chat():
    """Proxy SSE streaming from the Groq API back to the client UI."""
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    # Format incoming history for Groq messages requirement
    messages = [
        {
            'role': 'system',
            'content': (
                'You are DeepAI, a friendly and helpful assistant designed with a clean modern UI. '
                'Write clearly and concisely.'
            )
        }
    ]
    
    # Append past conversation context
    for msg in history:
        messages.append({'role': msg.get('role'), 'content': msg.get('content')})

    # Append the new user message
    messages.append({'role': 'user', 'content': user_message})

    def generate():
        # Yield padding for buffer issues on some servers (Windows/Werkzeug)
        yield ':' + ' ' * 2048 + '\n\n'

        try:
            stream = groq_client.chat.completions.create(
                model=MODEL,
                messages=messages,
                stream=True,
                max_tokens=4096,
                temperature=0.7,
            )
            for chunk in stream:
                token = chunk.choices[0].delta.content or ''
                if token:
                    # Stream tokens back in SSE format identical to how frontend expects
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': token}}]})}\n\n"

        except Exception as e:
            # We don't yield full objects here, just an error string to be picked up
            yield f"data: {json.dumps({'error': {'message': str(e)}})}\n\n"
            return

        # Tell client stream is done
        yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'X-Accel-Buffering': 'no',
            'Content-Type': 'text/event-stream; charset=utf-8'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, threaded=True, use_reloader=False)
