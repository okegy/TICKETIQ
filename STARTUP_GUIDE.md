# TicketIQ Root Build Instructions

To start the local stack:

1. **Start Databases:**
   ```bash
   docker-compose up -d
   ```

2. **Start Backend (Java Spring Boot):**
   ```bash
   cd backend
   ./gradlew bootRun
   ```

3. **Start AI Service (Python FastAPI):**
   ```bash
   cd ai-service
   .venv\Scripts\activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start Frontend (Angular):**
   ```bash
   cd frontend
   npm start
   ```
