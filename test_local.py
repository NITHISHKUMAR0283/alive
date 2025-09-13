#!/usr/bin/env python3
"""
Local testing for ARGO RAG Web System
Test the web interface locally before deploying
"""

import subprocess
import time
import requests
import sys
import os

def test_web_system():
    """Test the web backend directly"""
    print("Testing ARGO RAG Web System...")
    print("=" * 50)

    # Change to web backend directory
    backend_dir = os.path.join("web", "backend")
    if not os.path.exists(backend_dir):
        print("Error: web/backend directory not found")
        return False

    # Start the web server
    print("Starting web server...")
    try:
        # Run the backend server
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for server to start
        print("Waiting for server startup...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/api/status", timeout=2)
                if response.status_code == 200:
                    print("Server started successfully!")
                    break
            except:
                pass
            time.sleep(1)
            print(f"Waiting... {i+1}/30")
        else:
            print("Server startup timeout")
            process.terminate()
            return False

        # Wait for RAG system to load
        print("Waiting for RAG system to load...")
        for i in range(60):
            try:
                response = requests.get("http://localhost:8000/api/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("rag_loaded"):
                        print(f"RAG system loaded! ChromaDB: {data.get('chromadb_count', 0)} queries")
                        break
                    else:
                        print(f"RAG loading... {i+1}/60")
            except Exception as e:
                print(f"Checking status... {i+1}/60")
            time.sleep(2)
        else:
            print("RAG system load timeout")
            process.terminate()
            return False

        # Test a query
        print("Testing query...")
        try:
            query_data = {"query": "show me temperature data"}
            response = requests.post(
                "http://localhost:8000/api/query",
                json=query_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print("Query test successful!")
                print(f"Method: {result['method']}")
                print(f"Similarity: {result['similarity']:.3f}")
                print(f"Records: {result['total_records']}")
                print(f"Execution time: {result['execution_time']:.2f}s")
                print("\nWeb interface ready at: http://localhost:8000")

                # Keep server running
                print("\nServer is running. Press Ctrl+C to stop.")
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\nStopping server...")
                    process.terminate()
                    return True
            else:
                print(f"Query test failed: {response.text}")
                process.terminate()
                return False

        except Exception as e:
            print(f"Query test error: {e}")
            process.terminate()
            return False

    except Exception as e:
        print(f"Failed to start server: {e}")
        return False

if __name__ == "__main__":
    success = test_web_system()
    if success:
        print("Local testing completed successfully!")
    else:
        print("Local testing failed!")
        sys.exit(1)