# Voice Appointment Booking Agent — Setup (Arch Linux)

## 1. System dependencies

```bash
sudo pacman -Syu
sudo pacman -S python python-pip nodejs npm git base-devel
```

VS Code (you said it's already installed — skip if so). If not, via AUR:
```bash
sudo pacman -S --needed base-devel git
git clone https://aur.archlinux.org/yay.git
cd yay && makepkg -si
yay -S visual-studio-code-bin
```

Confirm versions:
```bash
python --version
node --version
npm --version
```

## 2. Backend setup

```bash
cd voice-appointment-agent/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
- `GROQ_API_KEY` — from console.groq.com
- `SUPABASE_URL` / `SUPABASE_KEY` — from your Supabase project settings → API
- `RESEND_API_KEY` — optional, from resend.com (skip if not testing email yet)
- Google Calendar vars — optional, fill in only when you get to that feature

Create the table in Supabase: open the SQL editor in your Supabase project dashboard and run everything in `backend/schema.sql`.

Run the backend:
```bash
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Check it's alive: `curl http://localhost:8000/health`

## 3. Frontend setup

```bash
cd voice-appointment-agent/frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000` in **Chrome** (Web Speech API support is best there — Firefox/Safari support is partial or absent).

## 4. Google Calendar (optional feature, do this last)

1. Go to Google Cloud Console → new project → enable "Google Calendar API".
2. Create OAuth 2.0 credentials (Desktop app type).
3. Use a short one-off Python script with `google-auth-oauthlib`'s `InstalledAppFlow` to run through the consent screen once and save the resulting credentials to `backend/google_token.json`.
4. `calendar_client.py` will pick that file up automatically on future runs.

## 5. Project layout

```
backend/     FastAPI app, state machine, integrations, config
frontend/    Next.js app — chat UI + dashboard
```

Everything about "what questions to ask" / "what business this is" lives in `backend/config/business_config.json` — edit that file, not the Python logic, to reconfigure the agent for a different business.

## 6. Common issues

- **Mic button does nothing** → use Chrome, and make sure the site has mic permission (check the address bar padlock).
- **CORS errors in browser console** → confirm `FRONTEND_ORIGIN` in backend `.env` matches the URL you're loading the frontend from.
- **Supabase insert fails** → check the table was created with `schema.sql` and your `SUPABASE_KEY` is the `anon` key (or `service_role` key if you disabled row-level security testing locally).
