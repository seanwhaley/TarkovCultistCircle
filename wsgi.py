"""WSGI entry point."""
from src.application import ApplicationFactory

app = ApplicationFactory.create_app()

if __name__ == "__main__":
    app.run()
