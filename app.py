from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    task = data.get('task', '').strip()

    if not task:
        return jsonify({'error': 'Task is required'}), 400

    prompt = f"""Design a complete multi-agent AI system for: "{task}"

Return ONLY valid JSON (no markdown, no backticks, no extra text). Use this exact schema:

{{
  "taskTitle": "string - clean title for the system",
  "taskDescription": "string - one line description",
  "agents": [
    {{
      "name": "string - agent name",
      "role": "string - short role descriptor",
      "icon": "string - single emoji",
      "inputs": ["string", "string", "string"],
      "outputs": ["string", "string"],
      "decisionLogic": ["string", "string"]
    }}
  ],
  "routingRules": [
    {{ "from": "string", "to": "string", "condition": "string" }}
  ],
  "validationGate": {{
    "question": "string",
    "onSuccess": "string",
    "onFailure": "string"
  }},
  "feedbackLoops": [
    {{ "title": "string", "steps": ["string", "string", "string", "string"] }}
  ],
  "failureHandling": [
    {{ "scenario": "string", "action": "string" }}
  ],
  "optimizations": [
    {{ "name": "string", "detail": "string" }}
  ],
  "scalabilityFeatures": [
    {{ "name": "string", "detail": "string" }}
  ]
}}

Requirements:
- 4 to 7 agents with distinct specialized roles
- All content must be specific to "{task}", not generic"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        start = raw.index('{')
        end = raw.rindex('}')
        json_str = raw[start:end+1]

        import json
        parsed = json.loads(json_str)
        return jsonify(parsed)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("✅ Server chal raha hai: http://localhost:5000")
    app.run(debug=True, port=5000)
