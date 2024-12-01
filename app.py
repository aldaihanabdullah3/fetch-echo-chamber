from flask import Flask, jsonify, render_template_string, request
import threading
import subprocess
import json
import random
from time import sleep

app = Flask(__name__)

# Dummy list of messages with speakers
messages = []

# List of speakers
speakers = ["Alice", "Bob", "Charlie", "Dave"]
topic = "No topic set"
# Read personas from config.json
with open('config.json', 'r') as f:
    config = json.load(f)
    speakers = [persona['name'] for persona in config['personas'].values()]
    topic = config['post']

speakers.append('Feedback')
speakers.append('')
# Assign a unique color to each speaker
speaker_colors = {speaker: f"#{random.randint(0, 0xFFFFFF):06x}" for speaker in speakers}

# Process for echo chamber simulation
echo_chamber_process = None

# HTML template for the initial UI
initial_template = f"""
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Set Topic - Echo Chamber</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Favicon -->
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* CSS Variables */
        :root {{
            --primary-color: #6200EE;
            --secondary-color: #03DAC5;
            --background-color: #F5F5F5;
            --text-color: #212121;
            --container-bg: #FFFFFF;
            --error-color: #B00020;
        }}

        body {{
            margin: 0;
            font-family: 'Roboto', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        header, footer {{
            background-color: var(--primary-color);
            color: #FFFFFF;
            text-align: center;
            padding: 20px 0;
        }}

        header h1 {{
            margin: 0;
            font-weight: 700;
        }}

        main {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        #topic-container {{
            background-color: var(--container-bg);
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 500px;
            box-sizing: border-box;
        }}

        #topic-container h2 {{
            margin-top: 0;
            font-weight: 400;
            color: var(--primary-color);
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }}

        textarea {{
            width: 100%;
            height: 120px;
            padding: 12px;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            font-size: 16px;
            resize: vertical;
            box-sizing: border-box;
            margin-bottom: 20px;
        }}

        button {{
            width: 100%;
            padding: 15px;
            background-color: var(--primary-color);
            border: none;
            border-radius: 4px;
            color: #FFFFFF;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}

        button:hover {{
            background-color: #3700B3;
        }}

        .error-message {{
            color: var(--error-color);
            margin-bottom: 15px;
            display: none;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 0 15px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Echo Chamber</h1>
    </header>

    <main>
        <div id="topic-container">
            <h2>Set the Topic to Start the Simulation</h2>
            <div class="error-message" id="error-message">Please enter a topic to start the simulation.</div>
            <label for="topic">Topic</label>
            <textarea id="topic" name="topic" placeholder="Enter the topic..." aria-label="Enter the topic">{topic}</textarea>
            <button id="start-button">Start Simulation</button>
        </div>
    </main>

    <footer>
        &copy; 2024 Echo Chamber Simulation
    </footer>

    <script>
        document.getElementById('start-button').addEventListener('click', function() {{
            const topic = document.getElementById('topic').value.trim();
            const errorMessage = document.getElementById('error-message');

            if (topic) {{
                errorMessage.style.display = 'none';

                fetch('/start_simulation', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{ topic: topic }})
                }})
                .then(response => {{
                    if (response.ok) {{
                        window.location.href = '/simulation';
                    }} else {{
                        throw new Error('Network response was not ok');
                    }}
                }})
                .catch(error => {{
                    console.error('Error starting simulation:', error);
                }});
            }} else {{
                errorMessage.style.display = 'block';
            }}
        }});
    </script>
</body>
</html>
"""

# HTML template for the chat UI
simulation_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chat UI - Echo Chamber Simulation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Favicon -->
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* CSS Variables */
        :root {
            --primary-color: #6200EE;
            --secondary-color: #03DAC5;
            --background-color: #F5F5F5;
            --text-color: #212121;
            --container-bg: #FFFFFF;
            --message-bg: #E3F2FD;
            --error-color: #B00020;
        }

        body {
            margin: 0;
            font-family: 'Roboto', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header, footer {
            background-color: var(--primary-color);
            color: #FFFFFF;
            text-align: center;
            padding: 20px 0;
        }

        header h1 {
            margin: 0;
            font-weight: 700;
        }

        main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        #chat-container {
            background-color: var(--container-bg);
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 600px;
            padding: 20px;
            box-sizing: border-box;
            overflow-y: auto;
            max-height: 70vh;
        }

        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 5px;
            background-color: var(--message-bg);
            display: flex;
            flex-direction: column;
        }

        .message .speaker {
            font-weight: 700;
            margin-bottom: 5px;
        }

        button {
            padding: 15px 20px;
            border: none;
            border-radius: 4px;
            background-color: var(--primary-color);
            color: #FFFFFF;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin: 20px auto;
            display: block;
            width: 200px;
        }

        button:hover {
            background-color: #3700B3;
        }

        @media (max-width: 600px) {
            main {
                padding: 10px;
            }

            #chat-container {
                padding: 15px;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Echo Chamber Chat</h1>
    </header>

    <main>
        <div id="chat-container" role="log" aria-live="polite">
            <div id="messages"></div>
        </div>
    </main>

    <button id="stop-button">Stop Simulation</button>

    <footer>
        &copy; 2024 Echo Chamber Simulation
    </footer>

    <script>
        let simulationInterval;

        async function fetchMessages() {
            try {
                const response = await fetch('/messages');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const messages = await response.json();
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '';
                messages.forEach(msg => {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';

                    const speakerSpan = document.createElement('span');
                    speakerSpan.className = 'speaker';
                    speakerSpan.textContent = msg.speaker;
                    speakerSpan.style.color = msg.color || 'var(--text-color)';

                    const textSpan = document.createElement('span');
                    textSpan.className = 'text';
                    textSpan.textContent = msg.text;

                    messageDiv.appendChild(speakerSpan);
                    messageDiv.appendChild(textSpan);

                    messagesDiv.appendChild(messageDiv);
                });
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                console.error('Error fetching messages:', error);
            }
        }

        function startFetchingMessages() {
            fetchMessages(); // Fetch immediately on load
            simulationInterval = setInterval(fetchMessages, 2000);
        }

        function stopSimulation() {
            clearInterval(simulationInterval);
            fetch('/stop_simulation', { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/';
                    } else {
                        throw new Error('Failed to stop simulation');
                    }
                })
                .catch(error => {
                    console.error('Error stopping simulation:', error);
                });
        }

        document.getElementById('stop-button').addEventListener('click', stopSimulation);
        window.addEventListener('load', startFetchingMessages);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(initial_template)

@app.route('/simulation')
def simulation():
    return render_template_string(simulation_template)

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global echo_chamber_process, messages
    data = request.get_json()
    topic = data.get('topic', 'No topic set')
    # Clear the messages
    messages = []
    # Start the echo_chamber.py script
    echo_chamber_process = subprocess.Popen(['python', 'echo_chamber.py', topic, 'localhost:5000'])
    return '', 204

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    global echo_chamber_process, messages
    if echo_chamber_process:
        echo_chamber_process.terminate()
        echo_chamber_process = None
        messages = []
        sleep(5)
    return '', 204

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    speaker = data.get('speaker')
    text = data.get('text')
    print(f"Received message from {speaker}: {text}")
    if speaker and text:
        messages.append({"speaker": speaker, "text": text})
    return '', 204

@app.route('/messages', methods=['GET'])
def get_messages():
    # Add color information to each message
    colored_messages = [{"speaker": msg["speaker"], "text": msg["text"], "color": speaker_colors[msg["speaker"]]} for msg in messages]
    return jsonify(colored_messages)

if __name__ == '__main__':
    app.run(debug=False)
