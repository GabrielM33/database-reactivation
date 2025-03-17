# Database Reactivation Backend

This backend service powers the Database Reactivation project, which aims to re-engage dormant leads through automated SMS conversations powered by LLM technology.

## Features

- **CSV Data Processing**: Import and export lead data from CSV files
- **LLM-Powered Conversations**: Generate contextually appropriate SMS messages
- **Twilio SMS Integration**: Send and receive SMS messages
- **Conversation State Management**: Track and manage conversation states
- **Concurrent Conversations**: Support multiple concurrent conversations
- **RESTful API**: Manage leads, conversations, and messages

## Setup

### Prerequisites

- Python 3.13 or higher
- Poetry (Python package manager)
- OpenAI API key
- Twilio account with SMS capabilities

### Installation

1. Clone the repository
2. Navigate to the backend directory:
   ```
   cd backend
   ```
3. Install dependencies with Poetry:
   ```
   poetry install
   ```
4. Create an environment file by copying the example:
   ```
   cp .env.example .env
   ```
5. Edit the `.env` file and fill in your API keys and configuration

### Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number for sending SMS
- `BOOKING_LINK`: The link to share with leads for booking calls
- `DATABASE_URL`: Database connection string (default: SQLite)
- `HOST`: Host to run the API server on (default: 0.0.0.0)
- `PORT`: Port for the API server (default: 8000)
- `ENV`: Environment mode (development or production)

## Usage

### Running the Application

Start the application with Poetry:

```
poetry run start
```

Or activate the virtual environment and run:

```
poetry shell
python -m backend.main
```

The API server will start on the configured host and port.

### API Endpoints

The API provides the following endpoints:

- **GET /**: API health check
- **POST /import-leads**: Import leads from a CSV file
- **GET /leads**: List all leads with optional filtering
- **GET /conversations**: List conversations with optional filtering
- **GET /conversations/{id}/messages**: Get messages for a conversation
- **POST /send-message**: Send a manual message to a lead
- **POST /webhook/twilio**: Webhook for receiving SMS from Twilio
- **POST /start-scheduler**: Start the conversation scheduler
- **POST /stop-scheduler**: Stop the conversation scheduler
- **POST /export-leads**: Export all leads to a CSV file

### CSV Import Format

The CSV file for importing leads should have the following columns:

- `name`: Lead's name (required)
- `phone_number`: Lead's phone number (required)
- `email`: Lead's email (optional)
- Additional columns will be stored as additional_info

### Twilio Webhook Setup

To receive SMS messages, configure your Twilio phone number to send a webhook to your API endpoint:

```
https://your-api-domain/webhook/twilio
```

## Development

### Running Tests

```
poetry run pytest
```

### Code Formatting

```
poetry run black backend
poetry run isort backend
```

### Type Checking

```
poetry run mypy backend
```

## License

This project is licensed under the terms of the license included with this repository.
