# Document Analysis Agent

A full-stack application that uses AI and ML to analyze documents and answer questions about their content.

## Features

- Document upload and processing
- Natural Language Processing for question answering
- Voice response generation
- Vector-based document search
- Modern web interface

## Tech Stack

- Backend: Python, FastAPI
- Frontend: React.js
- AI/ML: Transformers, NLP models
- Containerization: Docker

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started

1. Clone the repository:
```bash
git clone <your-repository-url>
cd voice_reporter
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Project Structure

```
.
├── backend/             # FastAPI backend
├── frontend/           # React frontend
├── uploads/            # Document upload directory
├── audio_output/       # Generated audio files
├── vector_storage/     # Vector embeddings storage
├── model_cache/        # Cached ML models
└── docker-compose.yml  # Docker configuration
```

## Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

## License

[Your chosen license]

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 