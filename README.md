# AIxMultimodal

A full-stack application with Next.js frontend and FastAPI backend.

## Project Structure

```
AIxMultimodal/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm or yarn

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

The backend API will be available at [http://localhost:8000](http://localhost:8000).

## Features

- **Frontend**: Next.js with Tailwind CSS for modern, responsive UI
- **Backend**: FastAPI for high-performance API development
- **Real-time**: WebSocket support for real-time communication
- **Modern UI**: Clean, responsive design with Tailwind CSS

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Development

### Frontend Development

The frontend uses:
- **Next.js 14**: React framework with App Router
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Type-safe JavaScript

### Backend Development

The backend uses:
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License. 