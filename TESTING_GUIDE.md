# TourStats - Testing Guide

## 🎯 Quick Start

All services are now running locally on your machine. Here's what you have and how to test each component:

## 📊 Running Services

| Service | URL | Description |
|---------|-----|-------------|
| **Web Client** | http://localhost:3000 | React chat interface + statistics dashboard |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Documentation** | http://localhost:8000/api/docs | Interactive Swagger UI |
| **Nanobot Agent** | ws://localhost:8001/ws | WebSocket AI chat agent |
| **PostgreSQL** | localhost:5432 | Database (internal) |
| **OpenTelemetry** | localhost:4317 | Observability (internal) |

## 🧪 How to Test Each Component

### 1️⃣ **Test the Web Client (React App)**

**Open in browser:** http://localhost:3000

**What you'll see:**
- A beautiful purple header with "🎯 TourStats"
- Two tabs: "💬 Chat" and "📊 Statistics"

**Testing steps:**
1. Click on **"💬 Chat"** tab
   - You should see a chat interface
   - Connection status should show "● Connected" (green)
   - Example messages at the bottom
   
2. Type a message like: "Just finished a tour with 15 people, mostly young adults around 25"
3. Press Enter or click "Send"
4. You should see the AI respond (loading animation → response)

5. Click on **"📊 Statistics"** tab
   - You'll see statistics cards (initially empty)
   - After adding excursions via chat, charts will appear
   - Shows: Total excursions, avg tourists, age, IT interest
   - Charts: Vivacity before/after, top interests pie chart
   - Correlation analysis section
   - Recent excursions table

---

### 2️⃣ **Test the Backend API**

**Open API docs:** http://localhost:8000/api/docs

**What you'll see:**
- Swagger UI with 3 endpoint groups:
  - `/api/excursions` - CRUD operations
  - `/api/chat` - AI chat endpoints
  - `/api/statistics` - Analytics endpoints

**Testing steps:**

#### Test Health Check:
1. Click `GET /api/health`
2. Click "Try it out" → "Execute"
3. You should see: `{"status": "healthy"}`

#### Test Create Excursion from Message:
1. Scroll to `POST /api/excursions/from-message`
2. Click "Try it out"
3. Enter this in the body:
   ```json
   {
     "message": "Just finished a tour with 20 tourists, average age 30. They were very energetic and super interested in tech parts, especially robotics and AI. Energy level dropped a bit after the tour."
   }
   ```
4. Click "Execute"
5. You should see the AI-extracted data:
   ```json
   {
     "number_of_tourists": 20,
     "average_age": 30.0,
     "vivacity_before": 0.8,
     "vivacity_after": 0.6,
     "interest_in_it": 0.9,
     "interests_list": "tech parts robotics AI",
     "confidence": 0.85
   }
   ```

#### Test Get Statistics:
1. Scroll to `GET /api/statistics/`
2. Click "Try it out" → "Execute"
3. You should see aggregated data:
   ```json
   {
     "total_excursions": 1,
     "avg_tourists_per_excursion": 20.0,
     "avg_age_all": 30.0,
     "avg_vivacity_before": 0.8,
     "avg_vivacity_after": 0.6,
     "avg_interest_in_it": 0.9,
     "top_interests": ["tech", "parts", "robotics", "ai"]
   }
   ```

#### Test Get Correlations:
1. Add 2-3 more excursions (use different ages/interests)
2. Call `GET /api/statistics/correlations`
3. You'll see correlation analysis between demographics and interests

---

### 3️⃣ **Test the Nanobot WebSocket Agent**

The nanobot is an AI agent that communicates via WebSockets.

**Testing with browser console:**
1. Open http://localhost:3000
2. Open browser DevTools (F12) → Console tab
3. The React app automatically connects to the nanobot
4. Send messages via the chat interface

**Testing with WebSocket client (advanced):**
```javascript
// In browser console or Node.js
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onopen = () => {
  console.log('Connected!');
  ws.send(JSON.stringify({
    type: 'chat',
    message: 'Hello, what can you do?'
  }));
};

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data));
};
```

**Expected response:**
```json
{
  "type": "welcome",
  "message": "Connected to TourStats AI Assistant"
}
```

Then your chat response:
```json
{
  "type": "chat_response",
  "message": "Hi! I can help you analyze excursion data..."
}
```

---

### 4️⃣ **Test Database (PostgreSQL)**

The database is running and storing data automatically.

**Check database is healthy:**
```bash
docker compose ps db
```
You should see: `healthy` status

**View logs:**
```bash
docker compose logs db
```

**Query data directly:**
```bash
docker compose exec db psql -U tourstats -d tourstats_db -c "SELECT * FROM excursions;"
```

---

### 5️⃣ **View All Service Logs**

**See what's happening:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f nanobot
docker compose logs -f client
docker compose logs -f db
```

---

## 🎬 Complete Demo Flow

Here's a step-by-step demo you can show to your TA:

### Step 1: Show the running app
```
Open: http://localhost:3000
```
- Show the beautiful UI
- Explain the two tabs (Chat + Statistics)

### Step 2: Add excursion data via AI
```
In chat, type: "Just finished a tour with 15 people, mostly young adults around 25. 
They were really energetic and super interested in tech parts, especially robotics and AI."
```
- Show how AI extracts structured data
- Explain the data model

### Step 3: Add another excursion
```
In chat, type: "Had 30 tourists today, average age 40. Moderate energy levels. 
Very interested in education history and culture, less interested in technology."
```

### Step 4: View statistics
```
Click on "📊 Statistics" tab
```
- Show the dashboard with charts
- Explain the correlation analysis
- Show the excursions table

### Step 5: Show the API
```
Open: http://localhost:8000/api/docs
```
- Show the interactive documentation
- Demonstrate a few API calls

### Step 6: Show it's all Dockerized
```bash
docker compose ps
```
- Show all services running
- Explain the architecture

---

## 🐛 Troubleshooting

### Chat shows "Disconnected"
- Check nanobot is running: `docker compose ps nanobot`
- View logs: `docker compose logs nanobot`
- Restart: `docker compose restart nanobot`

### API not responding
- Check backend: `docker compose ps backend`
- View logs: `docker compose logs backend`
- Restart: `docker compose restart backend`

### Need to reset everything
```bash
docker compose down -v  # Remove all containers and volumes
docker compose up -d    # Start fresh
```

### View database contents
```bash
docker compose exec db psql -U tourstats -d tourstats_db
\dt                    # List tables
SELECT * FROM excursions;  # View data
\q                     # Quit
```

---

## 📝 Example Messages to Try

1. **Basic excursion:**
   - "Had 10 tourists, average age 28"

2. **Detailed excursion:**
   - "Just finished with 25 people aged 20-35. Very high energy before and after. Extremely interested in IT (90%). Keywords: machine learning, startups, innovation"

3. **Ask for analysis:**
   - "Show me my statistics"
   - "What are the top interests?"
   - "Any correlations between age and IT interest?"

---

## 🚀 What You've Built

✅ **Backend:** FastAPI + PostgreSQL with AI-powered data extraction  
✅ **AI Agent:** Nanobot with WebSocket chat and MCP tools  
✅ **Frontend:** React app with real-time chat + analytics dashboard  
✅ **Infrastructure:** Docker Compose with 6 services  
✅ **Observability:** OpenTelemetry for monitoring  
✅ **API Docs:** Auto-generated Swagger UI  

**Total:** 42 files, ~2200 lines of code, 6 Docker containers

---

## 📞 Next Steps for Production

1. Add your Mistral API key to `.env`
2. Deploy to Ubuntu VM
3. Configure Caddy for HTTPS
4. Set up domain name
5. Enable authentication

But for the hackathon - **it's ready to demo!** 🎉
