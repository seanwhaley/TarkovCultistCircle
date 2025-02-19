import os
from src.application.app_factory import ApplicationFactory

# Determine the environment
env = os.getenv('FLASK_ENV', 'development')

# Create the application instance using the factory
app = ApplicationFactory.create_app(env)

# Run the application if this script is executed directly
if __name__ == '__main__':
    # Use the run_app method from the factory
    ApplicationFactory.run_app(app)
