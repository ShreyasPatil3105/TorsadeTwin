# TorsadeTwin Frontend

A dependency-light research workbench UI for the existing TorsadeTwin FastAPI backend.

## Run locally

Terminal 1 (existing backend; do not change its source):
```bash
cd ~/Downloads/TorsadeTwin_FINAL/TorsadeTwin_BACKEND
source .venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2:
```bash
cd ~/Downloads/TorsadeTwin_FINAL/TorsadeTwin_BACKEND
python frontend/dev_server.py
```

Open `http://127.0.0.1:5173`.

The dev server is a standard-library static server with a local reverse proxy for `/api/*`. It avoids changing FastAPI CORS configuration and keeps the scientific backend untouched.

## API
The UI consumes the existing endpoints:
- GET `/api/v1/health`
- GET `/api/v1/drugs`
- GET `/api/v1/scenarios`
- GET `/api/v1/validation`
- POST `/api/v1/simulate`
- POST `/api/v1/margin`
- POST `/api/v1/rescue`
- POST `/api/v1/blindspot`
- POST `/api/v1/verify`
- POST `/api/v1/report`

No scientific computation is implemented in the frontend.
