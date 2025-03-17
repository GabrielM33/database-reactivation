# Product Requirements Document (PRD)

## Database Reactivation Project

### 1. Project Overview

#### 1.1 Purpose

The Database Reactivation project aims to re-engage dormant leads from an existing database by utilizing an LLM to autonomously conduct SMS conversations. The ultimate goal is to encourage these leads to book sales calls through a provided link.

#### 1.2 Scope

- Update and process lead data from CSV files
- Implement an LLM-driven autonomous SMS messaging system
- Support concurrent conversations with 20-50 leads daily
- Track conversation states and outcomes
- Integrate with an existing NextJS UI

#### 1.3 Success Criteria

- System can successfully process and update lead data
- LLM can maintain contextually appropriate conversations with leads
- System can handle concurrent SMS conversations
- Leads successfully book sales calls through the provided link
- System provides accurate reporting on conversation outcomes

### 2. System Architecture

#### 2.1 High-Level Architecture

```
┌────────────┐    ┌─────────────┐    ┌───────────────┐    ┌───────────┐
│ CSV Data   │───>│ Data        │───>│ Conversation  │───>│ SMS       │
│ Processing │    │ Management  │    │ Engine (LLM)  │    │ Gateway   │
└────────────┘    └─────────────┘    └───────────────┘    └───────────┘
                        │                   ^                   │
                        │                   │                   │
                        v                   │                   v
                  ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
                  │ Database    │<───│ State        │<───│ Response     │
                  │             │    │ Management   │    │ Handler      │
                  └─────────────┘    └──────────────┘    └──────────────┘
```

#### 2.2 Core Components

1. **CSV Data Processor**: Handles importing, validating, and updating lead data
2. **Data Management**: Stores and retrieves lead information and conversation history
3. **Conversation Engine**: LLM-powered system that generates contextual messages
4. **SMS Gateway**: Handles sending and receiving SMS messages
5. **Response Handler**: Processes incoming messages from leads
6. **State Management**: Tracks conversation state and context for each lead
7. **Database**: Stores lead data, conversation history, and system configuration

### 3. Functional Requirements

#### 3.1 CSV Data Processing

- **FR1.1**: Import lead data from CSV files with fields including name, phone number, and relevant lead information
- **FR1.2**: Validate phone numbers and other critical fields
- **FR1.3**: Update existing lead records with new information
- **FR1.4**: Export updated lead data back to CSV format

#### 3.2 Data Management

- **FR2.1**: Store lead information in a structured database
- **FR2.2**: Track conversation history for each lead
- **FR2.3**: Record engagement metrics (response rates, booking rates)
- **FR2.4**: Support querying leads based on various criteria (last contact date, conversation status)

#### 3.3 LLM Conversation Engine

- **FR3.1**: Generate contextually appropriate SMS messages based on lead information and conversation history
- **FR3.2**: Maintain conversation context across multiple exchanges
- **FR3.3**: Recognize intent in lead responses (interest, questions, booking requests, opt-outs)
- **FR3.4**: Adjust tone and approach based on lead responses
- **FR3.5**: Include booking link at appropriate moments in the conversation

#### 3.4 SMS Messaging

- **FR4.1**: Send SMS messages to leads with appropriate throttling
- **FR4.2**: Receive and process incoming SMS messages
- **FR4.3**: Support concurrent conversations with multiple leads
- **FR4.4**: Handle SMS delivery issues and errors gracefully

#### 3.5 State Management

- **FR5.1**: Track conversation state for each lead (new, engaged, booked, opted-out)
- **FR5.2**: Manage conversation context and history
- **FR5.3**: Implement timeout and re-engagement logic for unresponsive leads
- **FR5.4**: Enforce compliance with messaging regulations (opt-out handling)

#### 3.6 Reporting and Analytics

- **FR6.1**: Track key performance metrics (response rate, booking rate)
- **FR6.2**: Generate reports on campaign effectiveness
- **FR6.3**: Identify patterns in successful conversations

### 4. Non-Functional Requirements

#### 4.1 Performance

- **NFR1.1**: Support concurrent messaging with 20-50 leads daily
- **NFR1.2**: Process incoming messages with minimal latency (<5 seconds)
- **NFR1.3**: Handle SMS sending and receiving at a rate of at least 10 messages per minute

#### 4.2 Scalability

- **NFR2.1**: Design system to handle future increases in lead volume
- **NFR2.2**: Support database growth without significant performance degradation

#### 4.3 Security

- **NFR3.1**: Secure storage of lead data and conversation history
- **NFR3.2**: Implement access controls for system functionality
- **NFR3.3**: Ensure compliance with data protection regulations

#### 4.4 Reliability

- **NFR4.1**: Implement error handling and recovery mechanisms
- **NFR4.2**: Log all system activities for troubleshooting
- **NFR4.3**: Implement automated backups of lead data and conversation history

#### 4.5 Compliance

- **NFR5.1**: Support opt-out mechanisms for leads
- **NFR5.2**: Comply with SMS messaging regulations
- **NFR5.3**: Maintain audit trails of all communications

### 5. Technical Specifications

#### 5.1 Technology Stack

- **Programming Language**: Python 3.9+
- **Database**: PostgreSQL or SQLite (for simpler deployments)
- **LLM Integration**: OpenAI API, Anthropic API, or similar
- **SMS Gateway**: Twilio API
- **State Management**: Redis or in-memory with database persistence
- **Concurrency**: Asyncio for handling multiple conversations

#### 5.2 Core Libraries

- **FastAPI/Flask**: API endpoints for the NextJS UI
- **Drizzle**: Database ORM
- **Pydantic**: Data validation
- **Twilio Python SDK**: SMS integration
- **OpenAI/Anthropic Python SDK**: LLM integration
- **Pandas**: CSV processing
- **APScheduler**: Scheduling and throttling message sending
- **Asyncio**: Asynchronous programming for concurrency
- **Logging**: Structured logging

#### 5.3 Key Interfaces

- **CSV Format**: Define expected CSV format and required fields
- **LLM Prompt Structure**: Define prompt templates and context formatting
- **SMS Message Format**: Define structure and constraints for messages
- **Database Schema**: Define tables for leads, conversations, messages

### 6. Implementation Plan

#### 6.1 Phase 1: Core Infrastructure

- Set up database schema
- Implement CSV import/export functionality
- Create basic lead management system
- Establish LLM integration

#### 6.2 Phase 2: Messaging System

- Implement SMS gateway integration
- Develop message sending and receiving logic
- Create conversation state management

#### 6.3 Phase 3: LLM Conversation Engine

- Develop context management
- Implement response generation logic
- Create intent recognition

#### 6.4 Phase 4: System Integration

- Connect all components
- Implement concurrency handling
- Develop error handling and recovery

#### 6.5 Phase 5: Testing and Optimization

- Test with sample lead data
- Optimize LLM prompts and conversation flow
- Performance testing and optimization

### 7. Additional Considerations

#### 7.1 LLM Conversation Guidelines

- Initial outreach should be friendly and non-pushy
- Responses should address lead questions or concerns
- System should recognize when to share the booking link
- Conversations should feel natural and personalized

#### 7.2 Error Scenarios

- Handle phone number formatting issues
- Plan for LLM API downtime
- Manage SMS delivery failures
- Strategy for handling inappropriate responses

#### 7.3 Data Privacy

- Ensure compliance with data protection regulations
- Implement data minimization principles
- Establish data retention policies

#### 7.4 Future Enhancements

- A/B testing of different conversation approaches
- Integration with CRM systems
- Expanded analytics and reporting
- Multi-channel communication (Email, WhatsApp)
