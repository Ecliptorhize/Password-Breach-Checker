# Password Breach Checker – Privacy OSINT Dashboard (Hybrid Legal Tool)

A local-only privacy dashboard that helps individuals check their own credentials against legal sources. The tool avoids any scraping or aggressive scanning and relies only on opt-in data sources.

## Legal + Ethical Notice
- This project is for personal cybersecurity assessments only.
- It must not be used for surveillance, doxxing, or scanning third parties without consent.
- No darknet/onion, social network scraping, or aggressive OSINT is implemented or permitted.

## Features
- **Email breach scanner** via HaveIBeenPwned (optional API key).
- **Password breach checker** using SHA-1 k-Anonymity against PwnedPasswords.
- **Local username/phone search** across user-provided TXT/CSV breach dumps.
- **Local image analysis** with InsightFace ArcFace ONNX (no external uploads).
- **AI privacy risk engine** producing a score, category, and recommendations.
- **Local dashboard** at `http://localhost:8080` powered by vanilla HTML/CSS/JS.

## Architecture
- **Backend:** FastAPI (Python) exposing REST endpoints.
- **Frontend:** Static HTML/CSS/JS served locally (or via any static file server).
- **AI:** ArcFace ONNX model executed locally with ONNX Runtime; falls back to pseudo-embeddings if the model is missing so the UI remains functional.
- **Data:** User-provided breach dumps stored under `data/breach-dumps/`.

```
password-breach-checker/
├── backend/
│   ├── main.py
│   ├── hibp_client.py
│   ├── password_checker.py
│   ├── breach_search.py
│   ├── ai_image_engine.py
│   ├── ai_risk_engine.py
│   ├── utils.py
│   ├── models/
│   │   └── arcface.onnx (placeholder, add your own model)
│   └── __init__.py
├── frontend/
│   ├── index.html
│   ├── dashboard.js
│   └── style.css
├── data/
│   └── breach-dumps/
├── requirements.txt
└── README.md
```

## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/yourname/password-breach-checker
   cd password-breach-checker
   ```
2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Add ArcFace model (optional but recommended)**
   - Place a legal ArcFace ONNX model file at `backend/models/arcface.onnx`.
   - Without the model, the app returns a pseudo-embedding so the API remains usable.

## Running the Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running the Frontend
- Serve `frontend/` with any static file server, for example:
  ```bash
  cd frontend
  python -m http.server 8080
  ```
- Open `http://localhost:8080` in your browser.

## Adding Local Breach Datasets
- Place your TXT or CSV files inside `data/breach-dumps/`.
- Use the dashboard uploader or copy files manually.
- Searches are case-insensitive and exact-match across lines/CSV cells.

## API Reference
- **POST /scan-email** `{ "email": "you@example.com", "api_key": "optional" }` → HIBP breaches + pastes.
- **POST /scan-password** `{ "password": "secret" }` → `{ "occurrences": <count> }`.
- **POST /scan-username** `{ "username": "handle" }` → `{ "query": str, "matches": {"file": ["lines"]} }`.
- **POST /scan-image** `{ "image_base64": "..." }` → embeddings + face count (local only).
- **POST /ai-report** aggregate previous results → `{ "score", "category", "recommendations" }`.
- **POST /upload-dataset** (multipart) → store TXT/CSV in `data/breach-dumps/`.

## Security Notes
- No data is transmitted to third-party services except HIBP and PwnedPasswords when invoked.
- Images are processed locally; remove temporary uploads after use.
- Protect your HIBP API key; do not hardcode it in the frontend.
- Use HTTPS or run locally; avoid exposing the service publicly.



## License
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
