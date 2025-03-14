import subprocess
import sys


def fix_dependencies():
    """
    Fix dependency conflicts by ensuring correct versions are installed
    """
    print("Fixing dependency conflicts...")

    # Create a virtual environment if it doesn't exist
    try:
        subprocess.run(["python", "-m", "venv", "venv"], check=True)
        print("Created virtual environment")
    except subprocess.CalledProcessError:
        print("Virtual environment already exists or couldn't be created")

    # Activate virtual environment and install dependencies
    if sys.platform.startswith("win"):
        pip_cmd = [".\\venv\\Scripts\\pip"]
    else:
        pip_cmd = ["./venv/bin/pip"]

    # Uninstall problematic packages first
    try:
        subprocess.run(
            [*pip_cmd, "uninstall", "-y", "google-generativeai"], check=False
        )
    except subprocess.CalledProcessError:
        pass

    # Install correct versions
    packages = [
        "Flask==2.0.1",
        "Werkzeug==2.0.1",
        "Jinja2==3.0.3",
        "google-generativeai>=0.3.1",
        "python-dotenv==0.19.0",
        "Markdown==3.3.7",
        "markdown-it-py==3.0.0",
        "aiofiles<22.0",
        "googlemaps",
        "geopy",
    ]

    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([*pip_cmd, "install", package], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")

    print("Dependencies fixed successfully!")


if __name__ == "__main__":
    fix_dependencies()
