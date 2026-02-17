# Samvidhan.ai - Bilingual Legal AI Assistant

A voice-enabled, bilingual legal RAG (Retrieval-Augmented Generation) assistant for Indian Law, powered by Google Gemini AI.

## 🌟 Features

- **Voice-First Interface**: Speak in Hindi or English using Web Speech API
- **RAG Pipeline**: Semantic search over Indian legal corpus (IPC, Constitution, etc.)
- **Premium 3D UI**: Glassmorphism design with animated backgrounds and 3D tilt effects
- **External Data Integration**: Real-time scraping from Indian Kanoon for extended coverage
- **Smart Model Fallback**: Automatically switches between Gemini models for reliability
- **Bilingual Support**: Full Hindi and English language support

## 🛠️ Tech Stack

### Frontend
- Next.js 16.1.6 (Turbopack)
- React
- TailwindCSS
- Framer Motion (3D animations)
- Web Speech API

### Backend
- FastAPI
- Python 3.9+
- ChromaDB (Vector database)
- Google Gemini API
- BeautifulSoup4 (Web scraping)

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google API Key (Gemini)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd samvidhan.ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   
   Create `backend/.env` file:
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Ingest Legal Data** (First time only)
   ```bash
   python ingest.py
   ```

5. **Start Backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Frontend Setup** (New terminal)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. **Open Application**
   
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
samvidhan.ai/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── rag_engine.py        # RAG logic & Gemini integration
│   ├── external_search.py   # Indian Kanoon scraper
│   ├── models.py            # Pydantic models
│   ├── ingest.py            # Data ingestion script
│   └── data/                # Legal corpus
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx     # Main chat interface
│   │   │   ├── layout.tsx   # App layout
│   │   │   └── globals.css  # Global styles
│   │   └── components/
│   │       ├── VoiceInput.tsx
│   │       ├── CitationCard.tsx
│   │       └── ThreeDBackground.tsx
│   └── package.json
└── README.md
```

## 🔑 API Endpoints

### `POST /query`
Submit a legal query and get AI-powered guidance.

**Request:**
```json
{
  "query": "What is the punishment for theft under IPC?",
  "language": "en"
}
```

**Response:**
```json
{
  "domain": "Criminal",
  "relevant_laws": ["IPC Section 379"],
  "explanation": "...",
  "general_guidance": "...",
  "confidence": "High",
  "disclaimer": "This is not legal advice.",
  "citations": [...]
}
```

## 🎨 UI Features

- **3D Glassmorphism**: Frosted glass panels with backdrop blur
- **Animated Background**: Floating colored orbs with smooth motion
- **Interactive Citations**: 3D tilt effect on hover
- **Voice Input Button**: Pulsating glow when active

## ⚠️ Important Notes

- **API Keys**: Never commit your `.env` file to GitHub
- **Legal Disclaimer**: This app provides general legal information, not legal advice
- **Rate Limits**: Gemini API has rate limits; the fallback mechanism handles this

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available for educational purposes.

## 🙏 Acknowledgments

- Google Gemini API
- Indian Kanoon for legal data
- Next.js and FastAPI communities

---

**Built with ❤️ for better access to legal information in India**
