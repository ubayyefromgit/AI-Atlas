# AI Atlas

AI Atlas is an AI-powered intelligence platform for the German Food & Beverage sector. It provides a modern interface to search, query, and discover AI companies relevant to the F&B industry, powered by a Grounded RAG (Retrieval-Augmented Generation) pipeline.

---

## 📋 Table of Contents

1. [What You'll Need (Prerequisites)](#what-youll-need-prerequisites)
2. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
   - [Step 1: Get the Project Files](#step-1-get-the-project-files)
   - [Step 2: Set Up Python Virtual Environment](#step-2-set-up-python-virtual-environment)
   - [Step 3: Configure API Keys (.env file)](#step-3-configure-api-keys-env-file)
   - [Step 4: Set Up the LLM (Choose One)](#step-4-set-up-the-llm-choose-one)
   - [Step 5: Initialize the Database](#step-5-initialize-the-database)
   - [Step 6: Import the Dataset](#step-6-import-the-dataset)
   - [Step 7: Build the Knowledge Base Index](#step-7-build-the-knowledge-base-index)
   - [Step 8: Set Up the Frontend](#step-8-set-up-the-frontend)
3. [Running the Application](#running-the-application)
4. [How to Use the App](#how-to-use-the-app)
5. [Architecture](#architecture)
6. [Completed Features](#completed-features)

---

## What You'll Need (Prerequisites)

Before you begin, please install the following tools on your computer. These are free downloads.

### 1. Python 3.11 or newer
Python is the programming language the backend is written in.
- **Download:** https://www.python.org/downloads/
- During installation on Windows, **check the box that says "Add Python to PATH"** — this is very important!
- To verify it installed correctly, open a terminal (Command Prompt or PowerShell on Windows) and type:
  ```bash
  python --version
  ```
  You should see something like `Python 3.11.x`.

### 2. Node.js 18 or newer
Node.js is used to run the frontend (the user interface).
- **Download:** https://nodejs.org/ (click the "LTS" version for stability)
- To verify, open a terminal and type:
  ```bash
  node --version
  ```
  You should see something like `v20.x.x`.

### 3. Git (Optional but recommended)
Git is used to download the project from source control.
- **Download:** https://git-scm.com/downloads

---

## Step-by-Step Setup Guide

> **Tip for beginners:** A "terminal" is just a text-based window you type commands into.
> - **Windows:** Press `Win + R`, type `powershell`, and press Enter.
> - **Mac/Linux:** Search for "Terminal" in your apps.

### Step 1: Get the Project Files

Open your terminal and navigate to a folder where you want to keep the project. For example:

```bash
# Go to your Desktop (optional, you can use any folder)
cd Desktop

# If you are cloning from Git:
git clone <your-repo-url>
cd AI-Atlas

# OR if you already downloaded the folder as a ZIP:
# Just open a terminal, navigate into the AI-Atlas folder
cd path\to\AI-Atlas
```

> **Note:** All commands from this point forward must be run from inside the `AI-Atlas` project folder.

---

### Step 2: Set Up Python Virtual Environment

A virtual environment is an isolated space for Python packages. Think of it as a dedicated toolbox for this project so packages don't conflict with other Python projects on your computer.

**Create the virtual environment:**
```bash
python -m venv venv
```

**Activate the virtual environment:**

- **Windows (PowerShell):**
  ```bash
  .\venv\Scripts\activate
  ```
- **Windows (Command Prompt):**
  ```bash
  venv\Scripts\activate.bat
  ```
- **Mac / Linux:**
  ```bash
  source venv/bin/activate
  ```

> ✅ **How to know it's activated:** Your terminal prompt will change to show `(venv)` at the beginning of the line, like `(venv) C:\Users\You\AI-Atlas>`.

**Install all Python dependencies:**
```bash
pip install -r requirements.txt
```
This will download and install all the Python packages the project needs. It may take a few minutes on the first run.

---

### Step 3: Configure API Keys (.env file)

The project uses a `.env` file to store secret keys like API keys. This file should never be shared publicly.

**Copy the example template:**

- **Windows (PowerShell):**
  ```bash
  Copy-Item .env.example .env
  ```
- **Mac / Linux:**
  ```bash
  cp .env.example .env
  ```

Now open the `.env` file in any text editor (Notepad, VS Code, etc.) and fill in the values:

```env
# --- Database ---
# Leave this as-is for a local SQLite database
DATABASE_URL=sqlite:///C:/Users/YOUR_USERNAME/Desktop/AI-Atlas/database/ai_atlas.db

# --- LLM API Keys (fill in the one you want to use) ---
GEMINI_API_KEY=        # Your Google Gemini API key (see Step 4)
GROQ_API_KEY=          # Your Groq API key (see Step 4)

# --- News & Discovery ---
NEWS_API_KEY=          # Optional: your GNews API key for live news
TAVILY_API_KEY=        # Optional: your Tavily key for AI discovery pipeline

# --- Other Settings (safe to leave as defaults) ---
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384
ADMIN_TOKEN=super_secret_admin_token
VITE_API_URL=http://127.0.0.1:8000
```

> **Important:** You only need to fill in the API key for the LLM you plan to use (see Step 4 below). The others can be left blank.

---

### Step 4: Set Up the LLM (Choose One)

The AI chat feature requires a Large Language Model (LLM) to generate answers. You have **three options** — pick the one that suits you best. You can switch between them any time inside the app using the dropdown in the Ask AI panel.

---

#### Option A: Google Gemini (Cloud - Free Tier Available)
Gemini is Google's AI model. It has a generous free tier.

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account and click **"Create API Key"**.
3. Copy the key and paste it into your `.env` file:
   ```env
   GEMINI_API_KEY=paste_your_key_here
   ```
4. In the app, select **"Gemini"** from the model dropdown in the Ask AI panel.

---

#### Option B: Groq (Cloud - Very Fast, Free Tier Available)
Groq offers blazing-fast inference using Llama3 models for free.

1. Go to **https://console.groq.com/** and sign up for a free account.
2. Navigate to **"API Keys"** in the sidebar and click **"Create API Key"**.
3. Copy the key and paste it into your `.env` file:
   ```env
   GROQ_API_KEY=paste_your_key_here
   ```
4. In the app, select **"Groq"** from the model dropdown in the Ask AI panel.

---

#### Option C: Ollama (100% Local & Free — No Internet Required)
Ollama runs an AI model entirely on your own computer. This is the best option if you want full privacy and no API keys, and your computer has at least 8GB of RAM.

1. **Download and install Ollama** from: https://ollama.com/download
   - Run the installer. On Windows, Ollama will add itself to your system tray.

2. **Download the Llama3 model.** Open a **new** terminal window and run:
   ```bash
   ollama run llama3
   ```
   This will download the model (~4GB). This only needs to be done once. After it's downloaded, it will start a chat session — you can type `/bye` to exit.

3. **Before asking a question in AI Atlas**, make sure Ollama is running. Just open a new terminal and run:
   ```bash
   ollama serve
   ```
   (Leave this terminal window open while using the app.)

4. In the app, select **"Ollama"** from the model dropdown in the Ask AI panel. No API key needed!

---

### Step 5: Initialize the Database

This creates the SQLite database file and all the necessary tables. Run this command **once** from the project root folder:

```bash
python scripts/init_db.py
```

You should see a confirmation that the database was created. A file called `ai_atlas.db` will appear in the `database/` folder.

---

### Step 6: Import the Dataset

This step loads the company data, problems, sectors, and mappings into the database.

**First, make sure your dataset CSV files are in the `data/atlas_dataset/` folder:**
- `companies_germany.csv`
- `problems_germany.csv`
- `problem_company_mapping.csv`
- `sectors_reference.csv`

**Then run the import script:**
```bash
python backend/scripts/ingest_dataset.py
```

After it finishes, you should see output confirming approximately:
- ✅ 116 Companies imported
- ✅ 71 Problems imported
- ✅ 15 Sectors imported
- ✅ 24 Mappings imported

> **If you want to start fresh**, you can wipe and re-import the data:
> ```bash
> python backend/scripts/ingest_dataset.py --reset --force
> ```

---

### Step 7: Build the Knowledge Base Index

This step reads all the company data and generates AI embeddings (mathematical representations of text) that power the semantic search and Ask AI features. The embedding model will be downloaded automatically on the first run (~90MB).

```bash
python backend/scripts/build_index.py --all
```

This may take a minute or two. You'll see progress bars as the embeddings are generated.

To verify everything indexed correctly:
```bash
python backend/scripts/build_index.py --verify
```

> **Note:** This step is "smart" — if you run it again later, it will only re-index data that has actually changed, skipping everything else.

---

### Step 8: Set Up the Frontend

Open a **new terminal window** (keep the current one open), navigate to the project folder, and run:

```bash
cd frontend
npm install
```

This installs all the JavaScript packages for the user interface. It may take a minute.

---

## Running the Application

You need **two terminal windows** open simultaneously to run the app.

### Terminal 1: Start the Backend

Make sure your virtual environment is activated (you'll see `(venv)` in the prompt). Then run:

```bash
cd backend
python -m uvicorn main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process...
```

🔗 **API Docs (Swagger UI):** http://127.0.0.1:8000/docs  
🔗 **Health Check:** http://127.0.0.1:8000/health

### Terminal 2: Start the Frontend

```bash
cd frontend
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in 300ms

  ➜  Local:   http://localhost:5173/
```

🔗 **Open the app in your browser:** http://localhost:5173

---

## How to Use the App

Once both servers are running, open **http://localhost:5173** in your browser.

### Dashboard
The homepage gives you an overview of the system: total companies indexed, AI categories, and system health status (Knowledge Base, News Engine, Discovery Pipeline).

### Company Directory
Navigate to the **Company Directory** from the sidebar to browse all 116+ AI companies. You can:
- Browse paginated company cards with logos, descriptions, and categories.
- Use the **Search Bar** at the top to filter by company name or AI category.
- Click any company card to see its full profile.

### Ask AI (Grounded RAG Chat)
Click the **Ask AI** button in the sidebar to open the AI chat panel.

1. **Select your LLM** from the dropdown in the panel header:
   - `Gemini` — Uses Google's Gemini model (requires `GEMINI_API_KEY` in `.env`)
   - `Groq` — Uses Llama3 via Groq's fast cloud (requires `GROQ_API_KEY` in `.env`)
   - `Ollama` — Uses your local Llama3 model (requires Ollama running in a terminal)

2. **Type your question**, for example:
   - *"Which companies specialize in Predictive Maintenance?"*
   - *"How does AWS help the F&B sector?"*
   - *"List all companies focused on robotics."*

3. The AI will answer **strictly based on the ingested dataset** — it won't make things up. Every response includes citations (e.g., `[S1]`, `[S2]`) pointing back to the source companies.

### Admin Panel (via Swagger UI)
Advanced users can access admin features at http://127.0.0.1:8000/docs.
- Click **"Authorize"** and enter the admin token: `admin1234`.
- Test endpoints like `/api/v1/admin/statistics` and `/api/v1/admin/discover`.

---

## Architecture

The system is built on a modern full-stack architecture:

```mermaid
flowchart TD
    User([User]) <--> Frontend[React Frontend\n(Vite + TypeScript)]
    Frontend <--> API[FastAPI Backend]
    
    subgraph Data Layer
        API <--> SQL[(SQLite DB\nStructured Metadata)]
        API <--> Vector[(ChromaDB\nSemantic Vectors)]
    end
    
    subgraph AI Pipeline
        API --> RAG[Ask AI Module\n(RAG Pipeline)]
        RAG <--> LLM[LLM API\n(Gemini / Claude)]
        RAG <--> Vector
    end
    
    subgraph Background Tasks
        Cron[Scheduler] --> Fetch[News Fetcher]
        Fetch --> LLMFilter[LLM Relevance Filter]
        LLMFilter --> SQL
        LLMFilter --> Vector
    end
```

| Layer | Technology |
|---|---|
| **Frontend** | React + Vite + TypeScript + Tailwind CSS |
| **Backend** | FastAPI + SQLAlchemy + Pydantic |
| **Database** | SQLite (relational data) |
| **Vector DB** | ChromaDB (semantic search embeddings) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` |
| **LLM (Cloud)** | Google Gemini / Groq (Llama3) |
| **LLM (Local)** | Ollama (Llama3 running on your machine) |

Detailed architecture documentation is in `docs/architecture.md`.

---

## Completed Features

- ✅ SQLite database schema with SQLAlchemy 2.0 ORM
- ✅ Abstract Repository layer for future extensibility
- ✅ Dataset ingestion pipeline (116 companies, 71 problems, 15 sectors)
- ✅ ChromaDB vector indexing with `sentence-transformers` embeddings
- ✅ Hybrid semantic + keyword search engine
- ✅ Grounded RAG pipeline (Gemini, Groq, Ollama)
- ✅ Structured AI responses with source citations
- ✅ Automated company news fetching (APScheduler)
- ✅ Admin dashboard with AI-driven company discovery pipeline
- ✅ Full REST API with pagination, filtering, and search
- ✅ Modern React frontend integrated with all backend services
