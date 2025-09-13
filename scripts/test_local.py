#!/usr/bin/env python3
"""
Local testing script for ARGO RAG Web System
Test your web interface before deploying
"""

import os
import sys
import subprocess
import time
import requests
import json

def test_local_deployment():
    """Test the web system locally"""
    print("🧪 Testing ARGO RAG Web System Locally")
    print("=" * 50)

    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is available")
    except:
        print("❌ Docker not found. Please install Docker first.")
        return

    # Build Docker image
    print("🔨 Building Docker image...")
    try:
        result = subprocess.run([
            "docker", "build", "-t", "argo-rag-web", "."
        ], check=True, capture_output=True, text=True)
        print("✅ Docker image built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e.stderr}")
        return

    # Run container
    print("🚀 Starting container...")
    try:
        # Kill any existing container
        subprocess.run([
            "docker", "stop", "argo-rag-test"
        ], capture_output=True)
        subprocess.run([
            "docker", "rm", "argo-rag-test"
        ], capture_output=True)

        # Start new container
        subprocess.Popen([
            "docker", "run", "--name", "argo-rag-test",
            "-p", "8000:8000", "argo-rag-web"
        ])

        print("✅ Container started on http://localhost:8000")

    except Exception as e:
        print(f"❌ Failed to start container: {e}")
        return

    # Wait for startup
    print("⏳ Waiting for RAG system to load...")
    for i in range(60):  # Wait up to 60 seconds
        try:
            response = requests.get("http://localhost:8000/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("rag_loaded"):
                    print("✅ RAG system loaded!")
                    break
                else:
                    print(f"🔄 Loading... ({i+1}/60)")
        except:
            print(f"🔄 Starting... ({i+1}/60)")
        time.sleep(1)
    else:
        print("❌ Timeout waiting for RAG system")
        return

    # Test query
    print("🧪 Testing query...")
    try:
        query_data = {"query": "show me temperature data"}
        response = requests.post(
            "http://localhost:8000/api/query",
            json=query_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            print(f"📊 Method: {result['method']}")
            print(f"📊 Similarity: {result['similarity']:.3f}")
            print(f"📊 Records: {result['total_records']}")
            print(f"🕐 Time: {result['execution_time']:.2f}s")
        else:
            print(f"❌ Query failed: {response.text}")

    except Exception as e:
        print(f"❌ Query test failed: {e}")

    print("\n🌐 Open http://localhost:8000 in your browser to test the web interface!")
    print("🛑 Press Ctrl+C to stop the test")

    try:
        input("\nPress Enter to stop the test container...")
    except KeyboardInterrupt:
        pass

    # Cleanup
    print("🧹 Cleaning up...")
    subprocess.run(["docker", "stop", "argo-rag-test"], capture_output=True)
    subprocess.run(["docker", "rm", "argo-rag-test"], capture_output=True)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_local_deployment()