#!/usr/bin/env python3
"""
Local web server for ARGO RAG system
Uses your existing RAG system with a simple HTTP server
"""

import os
import sys
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# Import your existing RAG system
from working_enhanced_rag import WorkingRAGSystem

class RAGWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path == '/api/status':
            self.serve_status()
        elif self.path.startswith('/api/query'):
            self.handle_query_get()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/query':
            self.handle_query_post()
        else:
            self.send_error(404)

    def serve_main_page(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ARGO RAG System - Local</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                .loading { background: #fff3cd; color: #856404; }
                .ready { background: #d4edda; color: #155724; }
                .error { background: #f8d7da; color: #721c24; }
                input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                button:disabled { background: #ccc; }
                .results { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
                .sql-code { background: #2d3748; color: #e2e8f0; padding: 10px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
                table { width: 100%; border-collapse: collapse; margin: 10px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>ARGO RAG System - Local Interface</h1>
            <div id="status" class="status loading">Initializing RAG system...</div>

            <div>
                <h3>Enter your query:</h3>
                <input type="text" id="queryInput" placeholder="e.g., show me temperature data for each profile" />
                <button id="queryBtn" onclick="submitQuery()" disabled>Submit Query</button>
            </div>

            <div id="results"></div>

            <script>
                function checkStatus() {
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {
                            const statusDiv = document.getElementById('status');
                            const queryBtn = document.getElementById('queryBtn');

                            if (data.rag_loaded) {
                                statusDiv.className = 'status ready';
                                statusDiv.innerHTML = 'RAG System Ready! ChromaDB: ' + data.chromadb_count + ' queries loaded';
                                queryBtn.disabled = false;
                            } else {
                                statusDiv.className = 'status loading';
                                statusDiv.innerHTML = 'Loading RAG system...';
                                setTimeout(checkStatus, 2000);
                            }
                        })
                        .catch(e => {
                            document.getElementById('status').innerHTML = 'Checking status...';
                            setTimeout(checkStatus, 2000);
                        });
                }

                function submitQuery() {
                    const query = document.getElementById('queryInput').value;
                    const resultsDiv = document.getElementById('results');
                    const queryBtn = document.getElementById('queryBtn');

                    if (!query.trim()) return;

                    queryBtn.disabled = true;
                    queryBtn.textContent = 'Processing...';
                    resultsDiv.innerHTML = '<div class="status loading">Processing your query...</div>';

                    fetch('/api/query', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query})
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.error) {
                            resultsDiv.innerHTML = '<div class="status error">Error: ' + data.error + '</div>';
                        } else {
                            displayResults(data);
                        }
                        queryBtn.disabled = false;
                        queryBtn.textContent = 'Submit Query';
                    })
                    .catch(e => {
                        resultsDiv.innerHTML = '<div class="status error">Request failed: ' + e + '</div>';
                        queryBtn.disabled = false;
                        queryBtn.textContent = 'Submit Query';
                    });
                }

                function displayResults(data) {
                    let html = '<div class="results">';
                    html += '<h4>Query: "' + data.query + '"</h4>';
                    html += '<p>Method: ' + data.method + ' | Similarity: ' + data.similarity.toFixed(3) + ' | Time: ' + data.execution_time.toFixed(2) + 's | Records: ' + data.total_records + '</p>';
                    html += '<h5>Generated SQL:</h5>';
                    html += '<div class="sql-code">' + data.sql + '</div>';
                    html += '<h5>Results (first 10 rows):</h5>';

                    if (data.data && data.data.length > 0) {
                        html += '<table><thead><tr>';
                        Object.keys(data.data[0]).forEach(key => {
                            html += '<th>' + key + '</th>';
                        });
                        html += '</tr></thead><tbody>';

                        data.data.slice(0, 10).forEach(row => {
                            html += '<tr>';
                            Object.values(row).forEach(val => {
                                html += '<td>' + (val !== null ? val : 'NULL') + '</td>';
                            });
                            html += '</tr>';
                        });
                        html += '</tbody></table>';

                        if (data.total_records > 10) {
                            html += '<p><em>... and ' + (data.total_records - 10) + ' more records</em></p>';
                        }
                    } else {
                        html += '<p>No data returned</p>';
                    }

                    html += '</div>';
                    document.getElementById('results').innerHTML = html;
                }

                // Allow Enter key
                document.getElementById('queryInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !document.getElementById('queryBtn').disabled) {
                        submitQuery();
                    }
                });

                // Start status check
                checkStatus();
            </script>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status(self):
        status = {
            "rag_loaded": hasattr(server_state, 'rag_system') and server_state.rag_system is not None,
            "chromadb_count": 0,
            "status": "loading"
        }

        if hasattr(server_state, 'rag_system') and server_state.rag_system:
            try:
                status["chromadb_count"] = server_state.rag_system.chroma_manager.collection.count()
                status["status"] = "ready"
            except:
                pass

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())

    def handle_query_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            query = data.get('query', '').strip()

            if not query:
                self.send_error(400, "No query provided")
                return

            if not hasattr(server_state, 'rag_system') or not server_state.rag_system:
                response = {"error": "RAG system not ready"}
            else:
                try:
                    start_time = time.time()
                    result = server_state.rag_system.process_query(query)
                    data, success = server_state.rag_system.execute_query(result.enhanced_sql)
                    execution_time = time.time() - start_time

                    if success:
                        response = {
                            "query": query,
                            "sql": result.enhanced_sql,
                            "data": data,
                            "method": result.method,
                            "similarity": result.similarity,
                            "execution_time": execution_time,
                            "total_records": len(data)
                        }
                    else:
                        response = {"error": "SQL execution failed"}
                except Exception as e:
                    response = {"error": str(e)}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, str(e))

class ServerState:
    def __init__(self):
        self.rag_system = None

server_state = ServerState()

def initialize_rag():
    """Initialize RAG system in background"""
    try:
        print("Initializing RAG System...")
        GROQ_API_KEY = "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"

        server_state.rag_system = WorkingRAGSystem(GROQ_API_KEY)

        # Setup ChromaDB
        try:
            current_count = server_state.rag_system.chroma_manager.collection.count()
            if current_count > 0:
                print(f"Using existing ChromaDB with {current_count} queries")
            else:
                print("ChromaDB is empty - setting up...")
                server_state.rag_system.setup_system()
        except Exception as e:
            print(f"Setting up ChromaDB: {e}")
            server_state.rag_system.setup_system()

        print("RAG System ready!")

    except Exception as e:
        print(f"RAG initialization failed: {e}")

def main():
    print("Starting ARGO RAG Local Web Server...")

    # Start RAG initialization in background
    rag_thread = threading.Thread(target=initialize_rag, daemon=True)
    rag_thread.start()

    # Start web server
    port = 8000
    server = HTTPServer(('localhost', port), RAGWebHandler)

    print(f"Server running at http://localhost:{port}")
    print("Opening browser...")

    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{port}')

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == "__main__":
    main()