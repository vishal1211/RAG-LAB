# RAG Lab — Frontend

React + TypeScript frontend for **RAG Lab**, a PDF question-answering application powered by a FastAPI retrieval-augmented generation (RAG) backend.

> **Live demo:** https://rag-lab-lovat.vercel.app/  
> **Source code:** https://github.com/vishal1211/RAG-LAB/tree/main
> **Backend API:** https://rag-lab-production.up.railway.app

## Features

- Upload a PDF for document ingestion.
- Ask questions about uploaded document content.
- Display generated answers and retrieved source context when supplied by the backend.
- Continue a chat using a session identifier for conversation-aware questions.
- Responsive React UI; production deployment on Vercel.

## Tech stack

- React, TypeScript, Vite
- FastAPI REST backend hosted separately
- Vercel hosting

## Repository layout

This README belongs in the `frontend/` directory of the RAG Lab monorepo:

```text
RAG-LAB/
├── frontend/
│   ├── src/
│   │   └── App.tsx
│   ├── package.json
│   └── README.md
└── backend/
```

The illustration shows the key files, not every file in the repository.

## Prerequisites

- Node.js compatible with the project's `package.json` and lockfile
- npm (or the package manager used by the repository)
- Running RAG Lab FastAPI backend, locally or on Railway

## Run locally

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite (usually `http://localhost:5173`). If using the hosted backend instead, set `VITE_API_BASE_URL=https://rag-lab-production.up.railway.app` and ensure that backend's CORS configuration permits the local frontend origin.

> **Important:** Confirm that `VITE_API_BASE_URL` is the exact environment variable referenced by your frontend source. Vite only exposes variables prefixed with `VITE_` to browser code.

## Build for production

```bash
npm run build
```

Vite normally writes production assets to `dist/`. Confirm the configured build scripts in `package.json`.

## Backend API used by the UI

| Action | Method | Path |
|---|---|---|
| Upload PDF | POST | `/api/v1/upload/file` |
| Ask question / search | POST | `/api/v1/upload/search` |
| API documentation | GET | `/docs` |
| Health status | GET | `/health` |

For the exact multipart fields, request body, and response schema, use the running backend's `/docs`: https://rag-lab-production.up.railway.app/docs. Do not assume the frontend and backend request shapes are interchangeable.

## Deploy to Vercel

1. Import the `RAG-LAB` repository.
2. Set **Root Directory** to `frontend`.
3. Use the **Vite** framework preset.
4. Build command: `npm run build`; output directory: `dist` (unless customized in your project).
5. Add the frontend environment variable:

   ```env
   VITE_API_BASE_URL=https://rag-lab-production.up.railway.app
   ```

6. Deploy, then add the **exact** Vercel origin to FastAPI `CORSMiddleware` and redeploy the backend if needed.

## Security notes

- Never place `GROQ_API_KEY`, `HUGGINGFACE_API_KEY`, or other secrets in a `VITE_` variable: Vite embeds those values into browser-delivered JavaScript.
- Browser-visible API URLs are not secrets.
- The deployed API should enforce upload size/type rules, rate limits, and access controls as appropriate before opening the demo to unrestricted traffic.

## Quick smoke test

1. Open the public frontend in a private/incognito window.
2. Upload a small, non-sensitive PDF.
3. Ask a question grounded in that PDF.
4. Ask a follow-up question that needs context.
5. Refresh and confirm the intended session/history behavior.
6. Check browser Network/Console for CORS and API errors.

## Learning focus

This frontend demonstrates integrating an AI backend into a user-facing product: document upload, asynchronous requests, conversation UX, error handling, and deployment. RAG retrieval and generation happen in the FastAPI backend.

## Future improvements

- Clear upload progress and structured API error messages.
- Explicit document and session management.
- Accessibility and responsive-layout checks.
- End-to-end tests for PDF upload and Q&A.

## License

Add your chosen license and a `LICENSE` file before publishing if you want to specify reuse permissions.
