# Provenance Guard

An AI-powered system for verifying and tracing the provenance of digital content using the Groq API and Flask.

## Features

- **Content Verification**: Analyze content authenticity using AI-powered verification
- **Provenance Tracking**: Trace the origin and history of information
- **Rate Limiting**: Built-in rate limiting to protect your API
- **RESTful API**: Easy-to-use endpoints for integration
- **Groq Integration**: Leverages fast Groq API for intelligent analysis

## Prerequisites

- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MAC-313/AI201-Project4.git
cd AI201-Project4
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create or update the `.env` file with your Groq API key:

```bash
GROQ_API_KEY=your_actual_api_key_here
```

**Important**: The `.env` file is already in `.gitignore` to prevent accidental exposure of your API key.

## Running the Application

```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Provenance Guard API"
}
```

### Verify Content

```http
POST /verify
Content-Type: application/json

{
  "content": "The text you want to verify"
}
```

**Response:**
```json
{
  "verified": true,
  "analysis": "Detailed analysis from Groq API",
  "request_id": "unique_request_id"
}
```

### Trace Provenance

```http
POST /trace
Content-Type: application/json

{
  "content": "The text to trace",
  "depth": 3
}
```

**Response:**
```json
{
  "origin": "Analyzed",
  "depth": 3,
  "analysis": "Provenance chain analysis from Groq API",
  "request_id": "unique_request_id"
}
```

## Rate Limiting

- **Global**: 200 requests per day, 50 per hour
- **/verify**: 10 requests per minute
- **/trace**: 5 requests per minute
- **/health**: 10 requests per minute

If you exceed rate limits, you'll receive a 429 error:

```json
{
  "error": "Rate limit exceeded",
  "message": "..."
}
```

## Example Usage

### Using curl

```bash
# Verify content
curl -X POST http://localhost:5000/verify \
  -H "Content-Type: application/json" \
  -d '{"content": "Sample text to verify"}'

# Trace provenance
curl -X POST http://localhost:5000/trace \
  -H "Content-Type: application/json" \
  -d '{"content": "Sample text to trace", "depth": 3}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Verify content
response = requests.post(
    f"{BASE_URL}/verify",
    json={"content": "Text to verify"}
)
print(response.json())

# Trace provenance
response = requests.post(
    f"{BASE_URL}/trace",
    json={"content": "Text to trace", "depth": 3}
)
print(response.json())
```

## Project Structure

```
AI201-Project4/
├── .env                 # Environment variables (not tracked in git)
├── .gitignore          # Git ignore file
├── requirements.txt    # Python dependencies
├── planning.md         # Project planning document
├── app.py              # Main Flask application
└── README.md           # This file
```

## Configuration

### Available Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)
- `FLASK_ENV`: Set to "production" for production deployment
- `FLASK_DEBUG`: Set to 0 for production

### Modifying Rate Limits

Edit the `@limiter.limit()` decorators in `app.py` to adjust rate limiting:

```python
@limiter.limit("10 per minute")  # Adjust this
def your_endpoint():
    pass
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (missing or invalid parameters)
- `429`: Rate limit exceeded
- `500`: Internal server error
- `503`: Service unavailable (Groq API not configured)

## Deployment

For production deployment:

1. Set `FLASK_ENV=production` and `FLASK_DEBUG=0`
2. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Configure SSL/TLS
4. Set up proper logging and monitoring

## Troubleshooting

### "GROQ_API_KEY not configured"
- Ensure you've created the `.env` file
- Verify the API key is set correctly
- Restart the application after updating `.env`

### Connection errors
- Check your internet connection
- Verify Groq API is accessible
- Check for network firewalls

### Rate limiting issues
- Wait for the time window to reset
- Adjust rate limits in `app.py` if needed
- Consider implementing caching for repeated requests

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Acknowledgments

- [Groq](https://groq.com) for the powerful LLM API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) for rate limiting

---

# Provenance Guard — AI Content Attribution System

Provenance Guard is built to solve a real problem: telling the difference between content written by humans and content generated by AI. In an era where AI output is increasingly polished and convincing, this matters for preserving attribution and keeping audience trust intact.

## How It Works

The system runs through a simple pipeline:

1. **You submit text** via the `/submit` endpoint
2. **We analyze it two ways**: An LLM examines the content semantically, and a stylometric function looks at the raw statistics (like how varied the vocabulary is, how complex the sentences get)
3. **We score the results**: Both signals get combined into a confidence score that maps to a transparency label
4. **We log everything**: The decision gets recorded in an audit log for accountability

## The Two Detection Approaches

- **LLM-based classification**: This catches the big-picture stuff—how the ideas flow, whether the language feels natural. It's good at understanding intent and context.
- **Stylometric heuristics**: This is more mechanical. It measures things like type-token ratio (basically vocabulary diversity) and sentence complexity. It won't fool easily, but it's also not great at understanding why something *feels* AI-generated.

## What You Get Back

The system returns one of three labels:

- **"This content shows strong indicators of AI generation"**: We're pretty confident it's AI.
- **"This content is consistent with human-written patterns"**: Looks human to us.
- **"Analysis is inconclusive; we cannot definitively classify the source"**: Could go either way, honestly.

## Rate Limits

We set limits at **10 requests per minute** and **100 per day**. This is a reasonable balance—it prevents someone from hammering the API while still supporting real usage from a content creator checking their own work.

## What We Added

Beyond the basic spec, we built an `/analytics` endpoint so you can track patterns: how often content gets flagged as AI, appeal rates, submission volume over time. Useful if you're running this at scale.

## A Note on Implementation

The main thing we had to fudge was ensuring the scoring function and logging pipeline talked to each other correctly. We added an explicit status check to make sure appeals got logged with the right "under_review" state—seemed like the kind of thing that would silently break in production if we didn't handle it explicitly.

## How We Built This

We used Claude to scaffold the Flask app and get Flask-Limiter set up (saves time on boilerplate). For the actual heuristic scoring logic, we also used Claude to optimize the thresholds so they'd line up nicely around 0.5 as the uncertainty midpoint. Then we tuned them by hand to make sure they felt right.
