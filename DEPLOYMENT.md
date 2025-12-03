# Deployment Guide

## 🐳 Docker Deployment (Recommended)

The easiest way to deploy the Precision Pharma AI Platform is using Docker Compose. This will spin up the API, Streamlit UI, and a Neo4j database.

### Prerequisites
- Docker & Docker Compose installed
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/shailendra6969/precision-pharma.git
   cd precision-pharma
   ```

2. **Configure Environment**
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   *Optional: Edit `.env` to add your OpenAI API key or change Neo4j credentials.*

3. **Build and Run**
   ```bash
   docker-compose up --build -d
   ```

4. **Access the Application**
   - **UI Dashboard**: [http://localhost:8501](http://localhost:8501)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (User: `neo4j`, Pass: `password`)

### Stopping the App
```bash
docker-compose down
```

---

## ☁️ Cloud Deployment

### Streamlit Community Cloud
1. Push your code to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub repository.
4. Set "Main file path" to `src/streamlit_app/main.py`.
5. Add your secrets (API keys, Neo4j URI) in the "Secrets" settings.

### Railway / Render / Heroku
This project includes a `Dockerfile` so it can be deployed to any container-based platform.
- **Build Command**: `docker build -t precision-pharma .`
- **Start Command**: The Dockerfile automatically starts both services, but for production, you might want to split them into separate services (one for API, one for UI) using the same image but overriding the `CMD`.
