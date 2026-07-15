# AI Customer Support - Agent Dashboard

> [!NOTE]
> For a detailed guide on the system architecture, Mixture-of-Experts (MoE) model tiers, LangGraph workflow, and cryptographic ledger verification, please refer to the main [project README](../README.md).

AI Customer Support is a multi-tier Mixture-of-Experts (MoE) customer support automation system with a LangGraph-powered backend and a Next.js frontend. It features automatic FAQ resolution, high-value request escalation to a human console, and a cryptographic audit ledger for execution trace validation.

---

## Getting Started

To run the project, you need to start both the Python backend and the Next.js frontend.

### 1. Run the Backend API

The backend is built with FastAPI and runs on port `8000`.

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Activate the virtual environment**:
   * **PowerShell (Windows)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * **CMD (Windows)**:
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   * **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

4. **Seed the Database** (optional, to reinitialize default customers, orders, and knowledge base):
   ```bash
   python seed.py
   ```

5. **Start the API server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

6. **Run Integration / Verification Tests**:
   To verify the API endpoints and test the MoE gating and cryptographic ledger:
   ```bash
   python verify.py
   ```

---

### 2. Run the Frontend Dashboard

The frontend is built with Next.js and runs on port `3000`.

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install npm dependencies**:
   ```bash
   npm install
   ```

3. **Start the Next.js development server**:
   ```bash
   npm run dev
   ```

4. **Open the browser**:
   Open [http://localhost:3000](http://localhost:3000) to view the AI Customer Support Dashboard and simulator console.

---

## Build for Production (Frontend)

To generate an optimized production build of the Next.js application:

```bash
npm run build
npm run start
```

