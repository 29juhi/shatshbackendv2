import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def seed_database():
    """Seed the database with sample data"""
    print("Seeding database...")
    from seed_data import seed_database
    seed_database()

def run_server():
    """Run the FastAPI server"""
    print("Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    try:
        # Install requirements
        install_requirements()
        
        # Seed database
        seed_database()
        
        # Run server
        run_server()
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
