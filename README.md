# Recipe App

## Local Docker Development

The default Docker setup runs the app against Firebase Auth and Firestore emulators, not your hosted Firebase project.

1. Start the app stack:

```bash
docker compose up --build
```

2. Open the app at `http://localhost:8501`.

3. Open the Firebase Emulator UI at `http://localhost:4000`.

The compose setup:

- bind-mounts the repo into the Streamlit container for live reload
- starts Firebase Auth and Firestore emulators in a separate container
- keeps emulator data in a named Docker volume so local state survives restarts

## Real Firebase Instead

If you want to run against your hosted Firebase project rather than the emulators, use a local `.streamlit/secrets.toml` based on `.streamlit/secrets.toml.example` and unset the emulator environment variables before starting the app.
