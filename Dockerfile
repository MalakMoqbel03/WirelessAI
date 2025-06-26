# ---------- Dockerfile ----------
FROM python:3.12-slim          #  ❶ base image
WORKDIR /app                   #  ❷ inside‐container working dir
COPY . .                       #  ❸ copy *everything* into /app
RUN pip install -r requirements.txt  # ❹ install deps
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]   # ❺ launch
