#!/usr/bin/env python3
"""
Working Enhanced RAG System - Uses fast local models for immediate testing
"""

import os
import json
import re
import duckdb
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import chromadb
import groq
from sentence_transformers import SentenceTransformer
import time

@dataclass 
class QueryResult:
    enhanced_sql: str
    method: str
    similarity: float
    execution_time: float
    metadata: Dict[str, Any]

class WorkingChromaManager:
    """ChromaDB manager using fast local model (all-MiniLM-L6-v2)"""
    
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token
        self.current_model = "sentence-transformers/all-MiniLM-L6-v2"
        self._init_fast_model()
        self._init_chromadb()
    
    def _init_fast_model(self):
        """Initialize fast, small embedding model"""
        try:
            print(f"[INFO] Loading fast embedding model: {self.current_model}")
            self.embedding_model = SentenceTransformer(self.current_model)
            print(f"[SUCCESS] Loaded fast model (dimension: {self.embedding_model.get_sentence_embedding_dimension()})")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise
    
    def _init_chromadb(self):
        """Initialize ChromaDB with fast embedding function"""
        self.client = chromadb.PersistentClient(path="./working_enhanced_chroma_db")
        self.collection_name = "working_optimized_argo_queries"
        
        # Fast embedding function with ChromaDB compatibility
        class FastEmbeddingFunction:
            def __init__(self, model):
                self.model = model
            
            def name(self):
                return "fast_sentence_transformers"
            
            def __call__(self, input):
                # Handle ChromaDB interface (single string or list)
                if isinstance(input, str):
                    input = [input]
                
                embeddings = self.model.encode(input, convert_to_tensor=False)
                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                return embeddings.tolist()
        
        self.embedding_function = FastEmbeddingFunction(self.embedding_model)
        
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"[INFO] Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Working optimized ARGO queries with fast embeddings"}
            )
            print(f"[INFO] Created new collection: {self.collection_name}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'model_name': self.current_model,
            'embedding_dim': self.embedding_model.get_sentence_embedding_dimension(),
            'api_based': False,
            'embedding_method': 'sentence_transformers_local'
        }
    
    def populate_with_optimized_data(self):
        """Load optimized data quickly"""
        try:
            with open('optimized_chromadb_data.json', 'r') as f:
                optimized_data = json.load(f)
        except FileNotFoundError:
            print("[ERROR] optimized_chromadb_data.json not found!")
            print("Run: python analyze_parquet_schema.py first")
            return
        
        queries = optimized_data['queries']
        print(f"[INFO] Loading {len(queries)} optimized queries with fast embeddings...")
        
        # Clear and recreate
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        # Process in reasonable batches
        batch_size = 50
        total_batches = (len(queries) - 1) // batch_size + 1
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"[INFO] Processing batch {batch_num}/{total_batches}...")
            
            ids = [q['id'] for q in batch]
            documents = [q['content'] for q in batch]
            metadatas = [q['metadata'] for q in batch]
            
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        
        print(f"[SUCCESS] Loaded {len(queries)} queries with fast embeddings!")
    
    def semantic_search(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """Perform semantic search"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            if results['documents'][0]:
                search_results = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    similarity = max(0.0, 1.0 - distance)
                    
                    search_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'rank': i + 1
                    })
                
                return search_results
            
            return []
            
        except Exception as e:
            print(f"[ERROR] Semantic search failed: {e}")
            return []

class WorkingRAGSystem:
    """Working RAG system with fast local embeddings"""
    
    def __init__(self, groq_api_key: str, hf_token: Optional[str] = None):
        print("[INFO] Initializing Working Enhanced RAG System...")
        
        # Initialize components
        self.chroma_manager = WorkingChromaManager(hf_token)
        self.query_engine = self._init_query_engine()
        
        # Initialize Groq client
        self.groq_client = groq.Groq(api_key=groq_api_key)
        
        print("[SUCCESS] Working RAG System ready!")
    
    def _init_query_engine(self):
        """Initialize DuckDB query engine"""
        conn = duckdb.connect()
        parquet_path = "./parquet_data"
        
        tables = {
            'floats': f"{parquet_path}/floats.parquet",
            'profiles': f"{parquet_path}/profiles.parquet",
            'measurements': f"{parquet_path}/measurements.parquet"
        }
        
        for table_name, file_path in tables.items():
            if os.path.exists(file_path):
                try:
                    conn.execute(f"""
                    CREATE OR REPLACE VIEW {table_name} AS 
                    SELECT * FROM read_parquet('{file_path}')
                    """)
                    print(f"[INFO] Setup table: {table_name}")
                except Exception as e:
                    print(f"[WARNING] Failed to setup {table_name}: {e}")
        
        return conn
    
    def setup_system(self):
        """Setup the system"""
        print("[INFO] Setting up ChromaDB with optimized data...")
        self.chroma_manager.populate_with_optimized_data()
        print("[SUCCESS] System setup complete!")
    
    def generate_sql(self, user_query: str, rag_context: List[Dict]) -> str:
        """Generate SQL using LLM"""
        context_parts = []
        for result in rag_context[:3]:
            context_parts.append(f"Context: {result['document']}")
            context_parts.append(f"Similarity: {result['similarity']:.3f}")
        
        context = "\n\n".join(context_parts)
        
        system_prompt = """You are an expert ARGO oceanographic database SQL generator.

DATABASE SCHEMA (DuckDB/Parquet):
- floats: float_id, wmo_number, current_status, deployment_date, deployment_latitude, deployment_longitude
- profiles: profile_id, float_id, profile_date, latitude, longitude, max_pressure
- measurements: measurement_id, profile_id, pressure, temperature, salinity, temperature_qc, salinity_qc

RULES:
1. Use exact column names from schema
2. Quality filters: temperature_qc <= 2, salinity_qc <= 2 for good data
3. Join pattern: FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id
4. NO LIMIT unless specifically requested
5. Return ONLY SQL, no explanations"""
        
        user_prompt = f"""Generate SQL for: "{user_query}"

Context:
{context}

Return only the SQL query."""
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            sql = response.choices[0].message.content.strip()
            sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'\s*```\s*$', '', sql)
            
            return sql.strip()
            
        except Exception as e:
            print(f"[ERROR] LLM failed: {e}")
            return ""
    
    def process_query(self, user_query: str) -> QueryResult:
        """Process query with optimized similarity"""
        start_time = datetime.now()
        
        # Semantic search
        rag_results = self.chroma_manager.semantic_search(user_query, top_k=5)
        
        # Get best similarity and SQL
        max_similarity = rag_results[0]['similarity'] if rag_results else 0.0
        rag_sql = ""
        
        if rag_results:
            best_doc = rag_results[0]['document']
            sql_patterns = [
                r'SQL Query:\s*(SELECT[^;]+(?:;|$))',
                r'SQL:\s*(SELECT[^;]+(?:;|$))',
                r'(SELECT[^;]+(?:;|$))'
            ]
            
            for pattern in sql_patterns:
                match = re.search(pattern, best_doc, re.IGNORECASE | re.DOTALL)
                if match:
                    rag_sql = match.group(1).strip().rstrip(';')
                    break
        
        # Enhanced similarity thresholds for better results
        if max_similarity >= 0.45 and rag_sql:  # Slightly lower threshold
            final_sql = rag_sql
            method = "rag_direct_high_similarity"
        elif max_similarity >= 0.25:  # Medium threshold
            llm_sql = self.generate_sql(user_query, rag_results)
            final_sql = llm_sql if llm_sql else rag_sql
            method = "llm_enhanced_medium_similarity"
        else:
            llm_sql = self.generate_sql(user_query, rag_results)
            final_sql = llm_sql
            method = "llm_generated_low_similarity"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResult(
            enhanced_sql=final_sql,
            method=method,
            similarity=max_similarity,
            execution_time=execution_time,
            metadata={
                'rag_results_count': len(rag_results),
                'embedding_model': self.chroma_manager.get_model_info()
            }
        )
    
    def execute_query(self, sql: str) -> Tuple[List[Dict], bool]:
        """Execute SQL query"""
        try:
            sql = sql.strip().rstrip(';')
            result = self.query_engine.execute(sql).fetchall()
            columns = [desc[0] for desc in self.query_engine.description]
            data = [dict(zip(columns, row)) for row in result]
            return data, True
        except Exception as e:
            print(f"[ERROR] Query execution failed: {e}")
            return [], False
    
    def test_and_execute(self, user_query: str, show_results: int = 5):
        """Test query and show results"""
        print(f"\n[QUERY] {user_query}")
        print("=" * 60)
        
        result = self.process_query(user_query)
        
        print(f"[METHOD] {result.method}")
        print(f"[SIMILARITY] {result.similarity:.4f}")
        print(f"[TIME] {result.execution_time:.3f}s")
        print(f"[MODEL] {result.metadata['embedding_model']['model_name']}")
        print(f"[SQL] {result.enhanced_sql}")
        
        if result.enhanced_sql:
            data, success = self.execute_query(result.enhanced_sql)
            
            if success and data:
                print(f"\n[SUCCESS] Retrieved {len(data)} records")
                for i, row in enumerate(data[:show_results]):
                    print(f"  {i+1}: {row}")
                if len(data) > show_results:
                    print(f"  ... and {len(data) - show_results} more")
            elif success:
                print("\n[INFO] Query executed but no data returned")
            else:
                print("\n[ERROR] Query execution failed")
        else:
            print("\n[ERROR] No SQL generated")
        
        return result

def main():
    """Test the working RAG system"""
    
    # Your API keys
    GROQ_API_KEY = "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"
    HF_TOKEN = "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"
    
    print("Working Enhanced RAG System Test")
    print("Using Fast Local Model + Optimized ChromaDB")
    print("=" * 60)
    
    try:
        # Initialize system
        rag_system = WorkingRAGSystem(GROQ_API_KEY, HF_TOKEN)
        
        # Setup system
        rag_system.setup_system()
        
        # Test queries to show similarity improvements
        test_queries = [
            "float_id",              # Should now get better similarity
            "get temperature",       # Should work well  
            "count floats",          # Should match well
            "salinity data",         # Should get good match
            "show profiles"          # Should work well
        ]
        
        print("\n" + "=" * 80)
        print("TESTING ENHANCED SEMANTIC SIMILARITY (FAST VERSION)")
        print("=" * 80)
        
        results = []
        for query in test_queries:
            result = rag_system.test_and_execute(query, show_results=3)
            results.append({
                'query': query,
                'similarity': result.similarity,
                'method': result.method
            })
            print("\n" + "-" * 60)
        
        # Summary
        print("\n" + "=" * 60)
        print("RESULTS SUMMARY") 
        print("=" * 60)
        
        high_sim = [r for r in results if r['similarity'] >= 0.4]
        print(f"High Similarity (≥0.4): {len(high_sim)}/{len(results)}")
        
        for r in results:
            status = "HIGH" if r['similarity'] >= 0.4 else "MEDIUM" if r['similarity'] >= 0.25 else "LOW"
            print(f"  '{r['query']}': {r['similarity']:.3f} ({status})")
        
        print(f"\nFast local embeddings working with optimized ChromaDB!")
        print(f"Ready to upgrade to API-based system when HF permissions are fixed.")
        
    except Exception as e:
        print(f"[ERROR] System failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()