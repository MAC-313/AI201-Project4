import sqlite3, uuid, os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

def init_db():
    conn = sqlite3.connect('provenance.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                    (id TEXT PRIMARY KEY, creator_id TEXT, attribution TEXT, 
                     confidence REAL, signal1 REAL, signal2 REAL, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute")
def submit():
    data = request.json
    content_id = str(uuid.uuid4())
    s1, s2 = 0.8, 0.9 
    confidence = (s1 + s2) / 2
    attribution = "likely_ai" if confidence > 0.5 else "likely_human"
    
    conn = sqlite3.connect('provenance.db')
    conn.execute('INSERT INTO logs VALUES (?, ?, ?, ?, ?, ?, ?)', 
                 (content_id, data['creator_id'], attribution, confidence, s1, s2, 'classified'))
    conn.commit()
    conn.close()
    
    return jsonify({"content_id": content_id, "attribution": attribution, "confidence": confidence})

@app.route("/appeal", methods=["POST"])
def appeal():
    content_id = request.json.get('content_id')
    conn = sqlite3.connect('provenance.db')
    conn.execute('UPDATE logs SET status = "under_review" WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "appeal_received"})

@app.route("/log", methods=["GET"])
def get_log():
    conn = sqlite3.connect('provenance.db')
    cursor = conn.execute('SELECT * FROM logs ORDER BY rowid DESC LIMIT 3')
    logs = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify({"entries": logs})

@app.route("/analytics", methods=["GET"])
def get_analytics():
    conn = sqlite3.connect('provenance.db')
    total = conn.execute('SELECT COUNT(*) FROM logs').fetchone()[0]
    ai_count = conn.execute('SELECT COUNT(*) FROM logs WHERE attribution = "likely_ai"').fetchone()[0]
    appeal_count = conn.execute('SELECT COUNT(*) FROM logs WHERE status = "under_review"').fetchone()[0]
    conn.close()
    return jsonify({"total_submissions": total, "ai_classified_count": ai_count, "total_appeals": appeal_count})

if __name__ == "__main__":
    app.run(debug=True)
