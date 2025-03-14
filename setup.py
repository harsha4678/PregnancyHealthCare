import os
import subprocess
import sys


def setup():
    """
    Complete setup script for the Pregnancy Healthcare app
    """
    print("Setting up Pregnancy Healthcare application...")

    # Create directories if they don't exist
    for directory in ["uploads", "logs"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

    # Fix dependencies
    print("Fixing dependencies...")
    if sys.platform.startswith("win"):
        subprocess.run(["python", "fix_dependencies.py"], check=True)
    else:
        subprocess.run(["python3", "fix_dependencies.py"], check=True)

    # Initialize the database
    print("Initializing database...")
    if sys.platform.startswith("win"):
        subprocess.run(["python", "init_db.py"], check=True)
    else:
        subprocess.run(["python3", "init_db.py"], check=True)

    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from .env.example...")
            with open(".env.example", "r") as example, open(".env", "w") as env:
                env.write(example.read())
            print("Created .env file. Please update it with your API keys.")
        else:
            print("Warning: .env.example file not found.")

    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    if sys.platform.startswith("win"):
        print("1. Activate the virtual environment: .\\venv\\Scripts\\activate")
        print("2. Start the app: python app.py")
    else:
        print("1. Activate the virtual environment: source ./venv/bin/activate")
        print("2. Start the app: python3 app.py")


if __name__ == "__main__":
    setup()
