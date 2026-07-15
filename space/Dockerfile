FROM python:3.12-slim

WORKDIR /app
COPY --chown=1000:1000 dist /app/dist

EXPOSE 7860
USER 1000
CMD ["python", "-m", "http.server", "7860", "--bind", "0.0.0.0", "--directory", "/app/dist"]
