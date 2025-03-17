# Database Reactivation Project

This project consists of a backend API for managing and automating conversations with leads, and a frontend dashboard for monitoring and managing these conversations.

## Deployment Options

### Option 1: Neon PostgreSQL + Vercel (Recommended)

#### Prerequisites

1. A Vercel account for the frontend (https://vercel.com)
2. A Neon account for the PostgreSQL database (https://neon.tech)
3. A Railway account for the backend API (https://railway.app)
4. Twilio account with SMS capabilities
5. OpenAI API key

#### Steps to Deploy

1. **Set up Neon PostgreSQL Database**

   - Sign up or log in to [Neon](https://neon.tech)
   - Create a new project
   - Create a new database for your application
   - Get your connection string from the dashboard (will look like `postgres://user:password@hostname/database`)

2. **Deploy the Backend to Railway**

   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will automatically detect the Dockerfile in the backend directory
   - Add the following environment variables in the Railway dashboard:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
     - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
     - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
     - `BOOKING_LINK`: Your booking link
     - `ENV`: Set to "production"
     - `DATABASE_URL`: Your Neon PostgreSQL connection string (from step 1)
     - `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (include your Vercel frontend URL)

3. **Deploy the Frontend to Vercel**

   - Go to [Vercel](https://vercel.com/dashboard)
   - Create a new project and import your GitHub repository
   - Set the root directory to `frontend`
   - Add the following environment variable:
     - `NEXT_PUBLIC_API_URL`: The URL of your Railway backend (e.g., https://your-app-name.railway.app)
   - Deploy the project

4. **Configure Twilio Webhook**
   - Log into your Twilio console
   - Go to Phone Numbers → Manage → Active numbers
   - Click on your Twilio phone number
   - Under "Messaging Configuration", set the webhook URL for "A MESSAGE COMES IN" to:
     - `https://your-railway-app-name.railway.app/webhook/twilio`
   - Make sure HTTP POST is selected
   - Save your changes

### Option 2: Railway for Both Backend and Database

You can also deploy both the backend and the PostgreSQL database on Railway.

1. Follow the steps in Option 1, but instead of using Neon:
2. In your Railway project, click "New" → "Database" → "PostgreSQL"
3. Railway will automatically add the `DATABASE_URL` environment variable to your project

## Local Development

1. **Clone this repository**

2. **Set up environment variables**

   ```
   cp backend/.env.example backend/.env
   ```

   Edit the `.env` file with your API keys and configuration.

3. **Set up local PostgreSQL (recommended) or use SQLite**

   - For PostgreSQL: Create a local database and update `DATABASE_URL` in your `.env` file
   - For SQLite: The default configuration will use SQLite

4. **Run with Docker Compose**

   ```
   docker-compose up
   ```

5. **Start the frontend**

   ```
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Project Structure

- `/backend`: FastAPI backend application
- `/frontend`: Next.js frontend application
- `Dockerfile`: Docker configuration for the backend
- `docker-compose.yml`: Docker Compose configuration for local development
- `railway.json`: Railway deployment configuration
