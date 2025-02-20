import os
from src.application.app_factory import create_app

# Determine the environment
env = os.getenv('FLASK_ENV', 'development')

# Create the application instance using the factory
app = create_app()

# Run the application if this script is executed directly
if __name__ == '__main__':
    # Use the run_app method from the factory
    ApplicationFactory.run_app(app)
