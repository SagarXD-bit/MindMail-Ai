# MailMind AI

### AI-Powered Email Automation & Intelligence Platform

MailMind AI is a full-stack email intelligence platform that turns a cluttered inbox into an actionable workspace. It fetches emails, analyzes them with AI, categorizes them by type and urgency, generates context-aware replies, tracks follow-ups, and provides response analytics.

Instead of simply displaying emails, MailMind helps answer:

> **What needs my attention, how urgent is it, and what should I reply?**

---

## Overview

MailMind combines a **React + TypeScript frontend**, **FastAPI backend**, **MySQL database**, **IMAP email integration**, and an **OpenAI-compatible AI layer**.

The application is designed around a simple workflow:

```mermaid
flowchart TD
    A[User Opens MailMind] --> B[Dashboard]

    B --> C[Fetch Emails]
    C --> D{Email Source}

    D -->|Connected Inbox| E[IMAP Server]
    D -->|Demo Mode| F[22 Sample Emails]

    E --> G[Email Processing]
    F --> G

    G --> H[AI Analysis]

    H --> I[Category]
    H --> J[Urgency]
    H --> K[Confidence Score]
    H --> L[Explanation]

    I --> M[Store / Update Email]
    J --> M
    K --> M
    L --> M

    M --> N[Email Workspace]

    N --> O[Search & Filters]
    N --> P[AI Reply]
    N --> Q[Follow-up]
    N --> R[Analytics]

    P --> S[Generate Reply]
    S --> T{User Review}

    T -->|Edit| U[Modify Reply]
    T -->|Regenerate| S
    T -->|Approve| V[Send Email]

    Q --> W[Reminder]
    W --> X[Snooze / Complete]

    R --> Y[Response Analytics]
```

---

## Core Features

### AI Email Categorization

MailMind analyzes incoming emails and assigns:

* **11 email categories**
* **4 urgency levels**
* AI confidence score
* Explanation for the classification

This allows users to quickly distinguish important messages from routine communication.

---

### AI Reply Engine

Generate context-aware responses without starting from a blank screen.

Supported tones:

* Professional
* Friendly
* Concise

Users can:

* Generate a reply
* Edit the generated response
* Regenerate it
* Copy the response
* Send it after explicit confirmation

```mermaid
flowchart LR
    A[Selected Email] --> B[AI Reply Engine]
    B --> C[Context Analysis]
    C --> D[Tone Selection]
    D --> E[Generated Reply]
    E --> F[Edit]
    E --> G[Regenerate]
    E --> H[Copy]
    E --> I[Send]
    I --> J[User Confirmation]
    J --> K[Email Sent]
```

MailMind never automatically sends an AI-generated reply without user confirmation.

---

## Follow-up Tracker

Important conversations can be converted into follow-ups.

Track:

* Pending follow-ups
* Reminders
* Overdue items
* Snoozed follow-ups
* Completed follow-ups

```mermaid
flowchart TD
    A[Email / Conversation] --> B[Create Follow-up]
    B --> C[Set Reminder]
    C --> D{Follow-up Status}

    D -->|Pending| E[Waiting]
    D -->|Due| F[Reminder]
    D -->|Overdue| G[Overdue]
    D -->|Snoozed| H[New Reminder Time]
    D -->|Completed| I[Complete]
```

---

## Response Analytics

MailMind provides a high-level view of email activity and response behavior.

Analytics include:

* Response rates
* Average response time
* Email volume
* Category distribution
* Urgency distribution
* AI classification accuracy metrics
* Follow-up activity

Charts are rendered using **Recharts**.

---

## Dashboard

The dashboard provides a centralized overview of the inbox.

### Dashboard includes

* KPI cards
* Email activity
* Category statistics
* Urgency statistics
* Response analytics
* Follow-up information
* Quick actions

The goal is to make the most important information visible without requiring the user to manually inspect every email.

---

## Email Search & Filtering

Emails can be searched and filtered using multiple attributes:

* Sender
* Subject
* Category
* Urgency
* Status
* Follow-up state

This allows users to quickly locate specific conversations inside a larger inbox.

---

## Email Integration

MailMind supports email retrieval through **IMAP** using Python's `imaplib`.

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as FastAPI
    participant I as IMAP Server
    participant AI as AI API
    participant DB as MySQL

    U->>F: Open inbox
    F->>B: Request emails
    B->>I: Authenticate / Fetch emails
    I-->>B: Email messages
    B->>AI: Analyze email
    AI-->>B: Category + urgency + confidence
    B->>DB: Store / update data
    DB-->>B: Saved data
    B-->>F: Processed emails
    F-->>U: Display inbox
```

### Demo Mode

MailMind also includes a **Demo Mode** with 22 realistic sample emails.

This allows the application to be explored without connecting a real mailbox.

---

# System Architecture

```mermaid
flowchart TB
    subgraph Client["Frontend"]
        A[React 18]
        B[Vite]
        C[TypeScript]
        D[Tailwind CSS]
        E[TanStack Query]
        F[Recharts]
    end

    subgraph API["Backend"]
        G[FastAPI]
        H[Pydantic v2]
        I[SQLAlchemy 2.0]
        J[API Routes]
        K[Email Services]
        L[AI Services]
    end

    subgraph Data["Data Layer"]
        M[(MySQL)]
    end

    subgraph External["External Services"]
        N[IMAP Email Server]
        O[OpenAI-Compatible API]
    end

    A --> J
    E --> J
    J --> G
    G --> H
    G --> I
    I --> M
    K --> N
    L --> O
    G --> K
    G --> L
```

---

# API Flow

The frontend communicates with the FastAPI backend through REST APIs.

```text
React Frontend
      │
      │ HTTP Request
      ▼
FastAPI Backend
      │
      ├── Email APIs
      ├── AI APIs
      ├── Follow-up APIs
      ├── Analytics APIs
      └── Database APIs
      │
      ▼
MySQL Database
```

For AI generation, the frontend communicates with the backend rather than exposing AI credentials in the browser.

Example:

```text
POST /api/generate
```

The backend processes the request and returns the generated result to the frontend.

---

# Tech Stack

| Layer                     | Technology                                              |
| ------------------------- | ------------------------------------------------------- |
| Frontend                  | React 18                                                |
| Build Tool                | Vite                                                    |
| Language                  | TypeScript                                              |
| Styling                   | Tailwind CSS                                            |
| Data Fetching             | TanStack Query                                          |
| Charts                    | Recharts                                                |
| Backend                   | Python + FastAPI                                        |
| Validation                | Pydantic v2                                             |
| ORM                       | SQLAlchemy 2.0                                          |
| Database                  | MySQL                                                   |
| AI                        | OpenAI-compatible API                                   |
| Email                     | IMAP / `imaplib`                                        |
| Authentication / Security | Environment-based secrets + encrypted email credentials |

---

# Project Structure

```text
MailMind-AI/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── ...
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── ...
│
└── README.md
```

---

# Local Development

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd MailMind-AI
```

---

## 2. Start the Backend

```bash
cd backend

python3 -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

## 3. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will provide the local frontend URL.

---

# Environment Variables

## Backend

Create:

```text
backend/.env
```

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/mailmind

OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

EMAIL_ENCRYPTION_KEY=your-fernet-key

APP_ENV=development
CORS_ORIGINS=*
```

## Frontend

Create:

```text
frontend/.env
```

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

For production, replace the local API URL with the deployed backend URL.

Example:

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

---

# API Documentation

FastAPI automatically generates interactive API documentation.

Once the backend is running:

```text
http://localhost:8000/docs
```

The Swagger interface can be used to inspect and test available API endpoints.

---

# Testing

MailMind includes automated tests covering the core backend functionality.

```bash
cd backend

source venv/bin/activate

python -m pytest tests/ -v
```

Current test coverage includes:

* API endpoints
* AI categorization
* Reply generation
* Analytics
* Backend functionality

---

# Deployment

## Frontend

The frontend is a Vite static application and can be deployed using:

* Vercel
* Netlify

Build:

```bash
npm run build
```

The production output is generated in the Vite build directory.

---

## Backend

The FastAPI backend can be deployed to platforms such as:

* Render
* Railway
* Fly.io

The deployed backend must provide:

* Python runtime
* FastAPI application server
* MySQL connectivity
* Required environment variables
* Correct CORS configuration

### Production Architecture

```mermaid
flowchart LR
    U[User] --> V[Vercel / Netlify]
    V --> F[React + Vite Frontend]

    F --> R[Render / Railway]
    R --> B[FastAPI Backend]

    B --> DB[(MySQL)]
    B --> AI[OpenAI-Compatible AI API]
    B --> IMAP[Email Provider / IMAP]
```

---

# Security

MailMind is designed so sensitive credentials remain on the backend.

### Security principles

* API keys are stored in environment variables
* Email passwords are encrypted at rest using Fernet
* Credentials are not exposed in frontend code
* Backend controls communication with external AI services
* AI-generated replies require explicit user confirmation
* Email credentials are not returned in normal API responses

---

# Application Workflow

The complete MailMind workflow can be summarized as:

```mermaid
flowchart TD
    A[Inbox] --> B[Fetch Emails]
    B --> C[Normalize Email Data]
    C --> D[AI Classification]

    D --> E[Category]
    D --> F[Urgency]
    D --> G[Confidence]
    D --> H[Explanation]

    E --> I[Email Workspace]
    F --> I
    G --> I
    H --> I

    I --> J{User Action}

    J -->|Search / Filter| I
    J -->|Generate Reply| K[AI Reply Engine]
    J -->|Create Follow-up| L[Follow-up Tracker]
    J -->|View Metrics| M[Analytics]

    K --> N[Review Reply]
    N --> O{Approved?}
    O -->|No| P[Edit / Regenerate]
    P --> N
    O -->|Yes| Q[Send Email]

    L --> R[Reminder]
    R --> S[Snooze / Complete]

    M --> T[Charts & KPIs]
```

---

# Why MailMind?

Traditional email clients primarily focus on **reading and sending messages**.

MailMind focuses on **understanding and acting on messages**.

```text
Traditional Inbox
        ↓
Read Email
        ↓
Decide What It Means
        ↓
Decide How Urgent It Is
        ↓
Write Reply
        ↓
Remember Follow-up
        ↓
Track Response
```

MailMind:

```text
Email
  ↓
AI Analysis
  ↓
Category + Urgency + Context
  ↓
Recommended Action
  ↓
AI Reply
  ↓
Human Approval
  ↓
Follow-up Tracking
  ↓
Response Analytics
```

---

# Key Design Principles

### Human-in-the-loop AI

AI assists with classification and response generation, while the user remains in control of final actions.

### Privacy-first architecture

Sensitive credentials and AI keys stay on the backend.

### Action-oriented interface

The application emphasizes what the user needs to **do**, rather than simply displaying more email data.

### Demo-friendly

Demo Mode makes it possible to evaluate the application without connecting a personal inbox.

### Responsive SaaS Experience

The interface is designed for desktop and mobile workflows.

---

# Project Status

MailMind AI currently provides:

* AI email categorization
* Urgency detection
* AI reply generation
* Multiple response tones
* Email search and filtering
* Follow-up tracking
* Response analytics
* IMAP integration
* Demo Mode
* REST API
* Interactive FastAPI documentation
* Responsive frontend

---

## License

Add your preferred license here.

---

## Built With

**React · TypeScript · FastAPI · Python · MySQL · SQLAlchemy · Pydantic · Tailwind CSS · TanStack Query · Recharts · IMAP · OpenAI-compatible APIs**
