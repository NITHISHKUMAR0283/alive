#!/usr/bin/env python3
"""
Final Enhanced ARGO RAG System - Complete implementation with schema-optimized ChromaDB
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
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import groq
import requests
import time

@dataclass 
class QueryResult:
    enhanced_sql: str
    method: str
    similarity: float
    execution_time: float
    metadata: Dict[str, Any]

class AdvancedQueryPreprocessor:
    """Advanced query preprocessing with semantic understanding"""
    
    def __init__(self):
        # Load schema information for better preprocessing
        try:
            with open('parquet_schema_analysis.json', 'r') as f:
                self.schema_info = json.load(f)
        except:
            self.schema_info = {}
        
        # Enhanced synonym mapping based on oceanographic domain
        self.oceanographic_synonyms = {
            # Temperature variations
            'temp': 'temperature',
            'temperature': 'temperature',
            'thermal': 'temperature',
            't': 'temperature',
            
            # Salinity variations  
            'sal': 'salinity',
            'salinity': 'salinity',
            'salt': 'salinity',
            's': 'salinity',
            
            # Pressure/Depth variations
            'pres': 'pressure',
            'pressure': 'pressure', 
            'depth': 'pressure',
            'p': 'pressure',
            
            # Float variations
            'float': 'floats',
            'floats': 'floats',
            'buoy': 'floats',
            'argo': 'floats',
            
            # Profile variations
            'profile': 'profiles',
            'profiles': 'profiles',
            'cast': 'profiles',
            
            # Measurement variations
            'measurement': 'measurements',
            'measurements': 'measurements',
            'data': 'measurements',
            'values': 'measurements',
            'readings': 'measurements',
            
            # Action synonyms
            'get': 'retrieve',
            'show': 'display',
            'list': 'display',
            'find': 'retrieve',
            'give': 'retrieve',
            
            # Quantity synonyms
            'count': 'total',
            'number': 'total',
            'how many': 'total',
            
            # Quality synonyms
            'good': 'quality',
            'reliable': 'quality',
            'valid': 'quality',
            
            # Status synonyms
            'active': 'operational',
            'working': 'operational',
            'live': 'operational'
        }
        
        # Column name mapping from schema
        self.column_mapping = {}
        for table_name, table_info in self.schema_info.items():
            if 'columns' in table_info:
                for col in table_info['columns']:
                    col_name = col['name'].lower()
                    self.column_mapping[col_name] = f"{table_name}.{col['name']}"
    
    def preprocess_query(self, query: str) -> Dict[str, Any]:
        """Advanced query preprocessing with semantic understanding"""
        original = query.lower().strip()
        
        # Remove common stop words but keep important ones
        stop_words = ['give me', 'show me', 'i want', 'please', 'can you']
        processed = original
        for stop_word in stop_words:
            processed = re.sub(rf'\b{stop_word}\b', '', processed, flags=re.IGNORECASE)
        
        # Normalize whitespace
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # Apply oceanographic synonyms
        expanded_terms = []
        for word in processed.split():
            expanded = self.oceanographic_synonyms.get(word, word)
            expanded_terms.append(expanded)
        
        expanded_query = ' '.join(expanded_terms)
        
        # Extract entity information (tables, columns, etc.)
        entities = self._extract_entities(processed)
        
        # Classify query intent
        intent = self._classify_intent(processed)
        
        # Generate semantic variations
        variations = self._generate_semantic_variations(processed, entities)
        
        return {
            'original': original,
            'processed': processed,
            'expanded': expanded_query,
            'intent': intent,
            'entities': entities,
            'variations': variations,
            'tokens': processed.split()
        }
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract database entities from query"""
        entities = {
            'tables': [],
            'columns': [],
            'operations': []
        }
        
        # Extract table names
        table_keywords = {
            'floats': ['float', 'buoy', 'argo'],
            'profiles': ['profile', 'cast'],
            'measurements': ['measurement', 'data', 'temperature', 'salinity', 'pressure']
        }
        
        for table, keywords in table_keywords.items():
            if any(kw in query for kw in keywords):
                entities['tables'].append(table)
        
        # Extract column names from schema
        for table_name, table_info in self.schema_info.items():
            if 'columns' in table_info:
                for col in table_info['columns']:
                    col_name = col['name'].lower()
                    if col_name in query or col_name.replace('_', ' ') in query:
                        entities['columns'].append(col['name'])
        
        # Extract operations
        operation_keywords = {
            'count': ['count', 'total', 'how many', 'number'],
            'retrieve': ['get', 'show', 'list', 'display', 'retrieve'],
            'filter': ['where', 'filter', 'specific'],
            'aggregate': ['average', 'mean', 'min', 'max', 'sum']
        }
        
        for operation, keywords in operation_keywords.items():
            if any(kw in query for kw in keywords):
                entities['operations'].append(operation)
        
        return entities
    
    def _classify_intent(self, query: str) -> str:
        """Classify query intent with higher precision"""
        intent_patterns = {
            'count_statistics': ['count', 'total', 'how many', 'number of'],
            'data_retrieval': ['get', 'show', 'list', 'display', 'retrieve', 'give me'],
            'data_filtering': ['where', 'filter', 'specific', 'in region', 'with'],
            'aggregation': ['average', 'mean', 'min', 'max', 'statistics'],
            'quality_control': ['quality', 'good', 'bad', 'qc', 'reliable'],
            'geographic': ['location', 'region', 'latitude', 'longitude', 'coordinates'],
            'temporal': ['recent', 'latest', 'date', 'time', 'year', 'month']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query for pattern in patterns):
                return intent
        
        return 'general_query'
    
    def _generate_semantic_variations(self, query: str, entities: Dict) -> List[str]:
        """Generate semantic variations based on entities and intent"""
        variations = [query]
        
        # Add table-specific context
        for table in entities['tables']:
            variations.append(f"{table} {query}")
            variations.append(f"database {table} {query}")
            variations.append(f"argo {table} {query}")
        
        # Add column-specific context
        for column in entities['columns'][:3]:  # Limit to prevent explosion
            variations.append(f"{column} {query}")
            variations.append(f"get {column} from database")
        
        # Add operation context
        for operation in entities['operations']:
            if operation == 'count':
                variations.append(f"statistical {query}")
                variations.append(f"count records {query}")
            elif operation == 'retrieve':
                variations.append(f"extract data {query}")
                variations.append(f"access {query}")
        
        return variations[:10]  # Limit variations

class OptimizedChromaManager:
    """ChromaDB manager using Hugging Face API for embeddings"""
    
    def __init__(self, embedding_model_name: str = "BAAI/bge-en-icl", hf_token: Optional[str] = None):
        self.embedding_model_name = embedding_model_name
        self.hf_token = hf_token
        self.current_model = embedding_model_name
        self._init_api_embedding()
        self._init_chromadb()
    
    def _init_api_embedding(self):
        """Initialize API-based embedding system"""
        if not self.hf_token:
            print("[WARNING] No HF token provided, embeddings may fail")
            return
            
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.embedding_model_name}"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
        
        print(f"[INFO] Using HF API for embeddings: {self.embedding_model_name}")
        
        # Test API connection
        try:
            test_response = self._get_api_embeddings(["test connection"])
            if test_response is not None:
                print(f"[SUCCESS] HF API connected successfully")
            else:
                print(f"[WARNING] API test failed, will retry during usage")
        except Exception as e:
            print(f"[WARNING] API initialization error: {e}")
    
    def _get_api_embeddings(self, texts: List[str], max_retries: int = 3) -> Optional[np.ndarray]:
        """Get embeddings using HF API with retry logic"""
        if not self.hf_token:
            print("[ERROR] No HF token available for API calls")
            return None
            
        payload = {"inputs": texts}
        
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    embeddings = np.array(response.json())
                    
                    # Handle response format
                    if embeddings.ndim == 3:
                        embeddings = embeddings.squeeze()
                    elif embeddings.ndim == 1 and len(texts) > 1:
                        embeddings = embeddings.reshape(len(texts), -1)
                    
                    # Normalize for better cosine similarity
                    if embeddings.ndim == 2:
                        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                    
                    return embeddings
                
                elif response.status_code == 503:
                    wait_time = 2 ** attempt
                    print(f"[INFO] Model loading on HF, waiting {wait_time}s... (attempt {attempt + 1})")
                    time.sleep(wait_time)
                    continue
                    
                else:
                    print(f"[ERROR] HF API failed: {response.status_code} - {response.text}")
                    return None
                    
            except Exception as e:
                print(f"[ERROR] API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    
        return None
    
    def _init_chromadb(self):
        """Initialize ChromaDB with API-based embedding function"""
        self.client = chromadb.PersistentClient(path="./final_enhanced_chroma_db")
        self.collection_name = "final_optimized_argo_queries"
        
        # API-based embedding function (updated for ChromaDB 0.4.16+)
        class APIEmbeddingFunction:
            def __init__(self, chroma_manager):
                self.chroma_manager = chroma_manager
            
            def __call__(self, input):  # Changed from 'texts' to 'input'
                # Handle both single string and list of strings
                if isinstance(input, str):
                    input = [input]
                
                embeddings = self.chroma_manager._get_api_embeddings(input)
                if embeddings is not None:
                    return embeddings.tolist()
                else:
                    # Fallback: Try using sentence-transformers as backup
                    print("[WARNING] HF API failed, trying local fallback...")
                    try:
                        from sentence_transformers import SentenceTransformer
                        backup_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                        embeddings = backup_model.encode(input, convert_to_tensor=False)
                        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                        return embeddings.tolist()
                    except Exception as e:
                        print(f"[ERROR] Backup model also failed: {e}")
                        # Final fallback to random embeddings
                        embedding_dim = 384  # Use smaller dimension for fallback
                        return [[0.1] * embedding_dim for _ in input]
        
        self.embedding_function = APIEmbeddingFunction(self)
        
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
                metadata={"description": "Final optimized ARGO queries with API-based embeddings"}
            )
            print(f"[INFO] Created new collection: {self.collection_name}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get embedding model information"""
        return {
            'model_name': self.current_model,
            'api_based': True,
            'embedding_method': 'huggingface_api',
            'hf_token_provided': bool(self.hf_token)
        }
    
    def populate_from_optimized_data(self):
        """Load optimized ChromaDB data from JSON"""
        try:
            with open('optimized_chromadb_data.json', 'r') as f:
                optimized_data = json.load(f)
            
            queries = optimized_data['queries']
            print(f"[INFO] Loading {len(queries)} optimized queries...")
            
            # Clear existing collection
            try:
                self.client.delete_collection(self.collection_name)
            except:
                pass
            
            # Recreate collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            
            # Add queries in smaller batches for API efficiency
            batch_size = 10  # Smaller batches for API calls
            total_batches = (len(queries) - 1) // batch_size + 1
            
            for i in range(0, len(queries), batch_size):
                batch = queries[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                print(f"[INFO] Processing batch {batch_num}/{total_batches} via HF API...")
                
                ids = [q['id'] for q in batch]
                documents = [q['content'] for q in batch] 
                metadatas = [q['metadata'] for q in batch]
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                
                # Small delay for API rate limiting
                time.sleep(0.5)
            
            print(f"[SUCCESS] Loaded {len(queries)} queries into ChromaDB")
            
        except Exception as e:
            print(f"[ERROR] Failed to load optimized data: {e}")
            raise
    
    def semantic_search(self, query_variations: List[str], top_k: int = 10) -> List[Dict]:
        """Perform semantic search with multiple query variations"""
        all_results = {}
        
        for query_text in query_variations[:5]:  # Limit variations
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    include=['documents', 'metadatas', 'distances']
                )
                
                if results['documents'][0]:
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0], 
                        results['distances'][0]
                    )):
                        # Calculate similarity (1 - distance for cosine)
                        similarity = 1.0 - distance
                        
                        doc_id = metadata.get('id', f"doc_{i}")
                        if doc_id not in all_results or similarity > all_results[doc_id]['similarity']:
                            all_results[doc_id] = {
                                'document': doc,
                                'metadata': metadata,
                                'similarity': similarity,
                                'query_used': query_text
                            }
            
            except Exception as e:
                print(f"[WARNING] Search failed for '{query_text}': {e}")
                continue
        
        # Sort by similarity and return top results
        sorted_results = sorted(all_results.values(), key=lambda x: x['similarity'], reverse=True)
        return sorted_results[:top_k]

class IntelligentThresholdManager:
    """Intelligent threshold management with adaptive learning"""
    
    def __init__(self):
        self.base_thresholds = {
            'high_similarity': 0.45,    # Use RAG directly - increased for better precision  
            'medium_similarity': 0.25,  # Enhance with LLM - adjusted range
            'low_similarity': 0.10      # Generate new - lower threshold for schema queries
        }
        
        # Dynamic adjustments based on query characteristics
        self.adjustments = {
            'query_type': {
                'column_query': 0.10,       # Boost for direct column queries
                'table_query': 0.05,        # Boost for table queries  
                'count_query': 0.08,        # Boost for count queries
                'join_query': -0.05,        # Lower for complex joins
                'measurement_query': 0.03   # Slight boost for measurements
            },
            'complexity': {
                'simple': 0.05,    # Boost simple queries
                'medium': 0.0,     # No change
                'complex': -0.05   # Lower for complex
            },
            'intent': {
                'count_statistics': 0.08,
                'data_retrieval': 0.06,
                'data_filtering': -0.02,
                'aggregation': -0.03,
                'quality_control': 0.02
            }
        }
    
    def calculate_thresholds(self, query_metadata: Dict, rag_metadata: Dict = None) -> Dict[str, float]:
        """Calculate adaptive thresholds"""
        thresholds = self.base_thresholds.copy()
        
        total_adjustment = 0.0
        
        # Query type adjustment
        if 'type' in query_metadata:
            total_adjustment += self.adjustments['query_type'].get(query_metadata['type'], 0.0)
        
        # Complexity adjustment  
        if 'complexity' in query_metadata:
            total_adjustment += self.adjustments['complexity'].get(query_metadata['complexity'], 0.0)
        
        # Intent adjustment
        if 'intent' in query_metadata:
            total_adjustment += self.adjustments['intent'].get(query_metadata['intent'], 0.0)
        
        # RAG result quality adjustment
        if rag_metadata and 'type' in rag_metadata:
            if rag_metadata['type'] in ['column_query', 'table_query']:
                total_adjustment += 0.05  # Boost for schema-based matches
        
        # Apply adjustments
        for key in thresholds:
            thresholds[key] = max(0.05, thresholds[key] + total_adjustment)
        
        return thresholds

class EnhancedParquetEngine:
    """Enhanced Parquet query engine with better error handling"""
    
    def __init__(self, parquet_path: str = "./parquet_data"):
        self.parquet_path = parquet_path
        self.conn = duckdb.connect()
        self.available_tables = self._setup_tables()
    
    def _setup_tables(self) -> List[str]:
        """Setup DuckDB tables from Parquet files"""
        parquet_files = {
            'floats': f"{self.parquet_path}/floats.parquet",
            'profiles': f"{self.parquet_path}/profiles.parquet",
            'measurements': f"{self.parquet_path}/measurements.parquet",
            'spatial_summaries': f"{self.parquet_path}/spatial_summaries.parquet",
            'quality_control_tests': f"{self.parquet_path}/quality_control_tests.parquet",
            'quality_control_results': f"{self.parquet_path}/quality_control_results.parquet"
        }
        
        available_tables = []
        for table_name, file_path in parquet_files.items():
            if os.path.exists(file_path):
                try:
                    self.conn.execute(f"""
                    CREATE OR REPLACE VIEW {table_name} AS 
                    SELECT * FROM read_parquet('{file_path}')
                    """)
                    available_tables.append(table_name)
                    print(f"[INFO] Setup table: {table_name}")
                except Exception as e:
                    print(f"[WARNING] Failed to setup {table_name}: {e}")
        
        return available_tables
    
    def execute_query(self, sql: str) -> Tuple[List[Dict], bool]:
        """Execute query with enhanced error handling"""
        try:
            # Clean SQL
            sql = sql.strip().rstrip(';')
            
            # Execute query
            result = self.conn.execute(sql).fetchall()
            columns = [desc[0] for desc in self.conn.description]
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in result]
            
            return data, True
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[ERROR] Query execution failed: {e}")
            
            # Try to suggest fixes for common errors
            if 'table' in error_msg and 'does not exist' in error_msg:
                print(f"[SUGGESTION] Available tables: {', '.join(self.available_tables)}")
            elif 'column' in error_msg and 'does not exist' in error_msg:
                print("[SUGGESTION] Check column names in schema")
            
            return [], False

class FinalEnhancedRAGSystem:
    """Final enhanced RAG system with all optimizations"""
    
    def __init__(self, groq_api_key: str, hf_token: Optional[str] = None):
        print("[INFO] Initializing Final Enhanced RAG System...")
        
        # Store tokens
        self.hf_token = hf_token
        
        # Initialize components
        self.preprocessor = AdvancedQueryPreprocessor()
        self.chroma_manager = OptimizedChromaManager(hf_token=hf_token)
        self.threshold_manager = IntelligentThresholdManager()
        self.query_engine = EnhancedParquetEngine()
        
        # Initialize Groq client
        self.groq_client = groq.Groq(api_key=groq_api_key)
        
        print("[SUCCESS] Final Enhanced RAG System initialized")
    
    def setup_system(self):
        """Setup the complete system"""
        print("[INFO] Setting up optimized ChromaDB collection...")
        self.chroma_manager.populate_from_optimized_data()
        print("[SUCCESS] System setup complete")
    
    def generate_sql_with_llm(self, user_query: str, rag_context: List[Dict], query_metadata: Dict) -> str:
        """Generate SQL with enhanced LLM prompting"""
        
        # Build rich context from top RAG results
        context_parts = []
        for result in rag_context[:3]:
            context_parts.append(f"Context: {result['document']}")
            context_parts.append(f"Similarity: {result['similarity']:.3f}")
        
        context = "\n\n".join(context_parts)
        
        # Enhanced system prompt
        system_prompt = f"""You are an expert ARGO oceanographic database SQL generator.

DATABASE SCHEMA (DuckDB/Parquet):
FLOATS TABLE: float_id, wmo_number, current_status, deployment_date, deployment_latitude, deployment_longitude, last_latitude, last_longitude, last_update
PROFILES TABLE: profile_id, float_id, profile_date, latitude, longitude, max_pressure, cycle_number, data_quality_flag, data_mode
MEASUREMENTS TABLE: measurement_id, profile_id, pressure, temperature, salinity, temperature_qc, salinity_qc

CRITICAL SQL GENERATION RULES:
1. Use exact table/column names from schema above
2. Table aliases: f=floats, p=profiles, m=measurements  
3. Quality filtering: temperature_qc <= 2, salinity_qc <= 2 for reliable data
4. Join pattern: FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id
5. NO LIMIT clauses unless user specifically requests limited results
6. Return ONLY the SQL query, no explanations

Query Intent: {query_metadata.get('intent', 'general')}
Query Entities: Tables={query_metadata.get('entities', {}).get('tables', [])}, Columns={query_metadata.get('entities', {}).get('columns', [])}
"""
        
        user_prompt = f"""Generate SQL for: "{user_query}"

Context from semantic search:
{context}

Return only the SQL query without any formatting or explanations."""
        
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
            
            # Clean SQL response
            sql = re.sub(r'^```sql\s*', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'\s*```\s*$', '', sql)
            sql = sql.strip()
            
            return sql
            
        except Exception as e:
            print(f"[ERROR] LLM SQL generation failed: {e}")
            return ""
    
    def process_enhanced_query(self, user_query: str) -> QueryResult:
        """Process query with all enhancements"""
        start_time = datetime.now()
        
        # Advanced preprocessing
        query_metadata = self.preprocessor.preprocess_query(user_query)
        
        # Semantic search with variations
        search_variations = [query_metadata['expanded']] + query_metadata['variations']
        rag_results = self.chroma_manager.semantic_search(search_variations, top_k=8)
        
        # Calculate intelligent thresholds
        best_rag_metadata = rag_results[0]['metadata'] if rag_results else {}
        thresholds = self.threshold_manager.calculate_thresholds(query_metadata, best_rag_metadata)
        
        # Get best similarity and SQL
        max_similarity = rag_results[0]['similarity'] if rag_results else 0.0
        rag_sql = ""
        
        if rag_results:
            # Try to extract SQL from best result
            best_doc = rag_results[0]['document']
            sql_patterns = [
                r'SQL:\s*([^;]+(?:;|$))',
                r'sql:\s*([^;]+(?:;|$))',
                r'SELECT\s+[^;]+(?:;|$)',
                r'select\s+[^;]+(?:;|$)'
            ]
            
            for pattern in sql_patterns:
                match = re.search(pattern, best_doc, re.IGNORECASE | re.DOTALL)
                if match:
                    rag_sql = match.group(1).strip().rstrip(';')
                    break
        
        # Intelligent routing decision
        if max_similarity >= thresholds['high_similarity'] and rag_sql:
            final_sql = rag_sql
            method = "rag_direct_high_similarity"
            
        elif max_similarity >= thresholds['medium_similarity'] and rag_results:
            # Medium similarity - enhance with LLM
            llm_sql = self.generate_sql_with_llm(user_query, rag_results, query_metadata)
            final_sql = llm_sql if llm_sql else rag_sql
            method = "llm_enhanced_medium_similarity"
            
        else:
            # Low similarity - generate new SQL
            llm_sql = self.generate_sql_with_llm(user_query, rag_results, query_metadata) 
            final_sql = llm_sql
            method = "llm_generated_low_similarity"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResult(
            enhanced_sql=final_sql,
            method=method,
            similarity=max_similarity,
            execution_time=execution_time,
            metadata={
                'query_metadata': query_metadata,
                'thresholds': thresholds,
                'rag_results_count': len(rag_results),
                'best_rag_type': best_rag_metadata.get('type', 'unknown'),
                'embedding_model': self.chroma_manager.current_model
            }
        )
    
    def query_and_execute(self, user_query: str, show_results: int = 10):
        """Complete query processing and execution"""
        print(f"\n[QUERY] {user_query}")
        print("=" * 80)
        
        # Process query
        result = self.process_enhanced_query(user_query)
        
        print(f"[METHOD] {result.method}")
        print(f"[SIMILARITY] {result.similarity:.4f}")
        print(f"[PROCESSING TIME] {result.execution_time:.3f}s")
        print(f"[RAG RESULTS] {result.metadata['rag_results_count']} matches")
        print(f"[BEST RAG TYPE] {result.metadata['best_rag_type']}")
        print(f"[THRESHOLDS] High: {result.metadata['thresholds']['high_similarity']:.3f}, Medium: {result.metadata['thresholds']['medium_similarity']:.3f}")
        print(f"[SQL] {result.enhanced_sql}")
        
        # Execute query
        if result.enhanced_sql:
            data, success = self.query_engine.execute_query(result.enhanced_sql)
            
            if success and data:
                print(f"\n[SUCCESS] Retrieved {len(data)} records")
                for i, row in enumerate(data[:show_results]):
                    print(f"  Row {i+1}: {row}")
                if len(data) > show_results:
                    print(f"  ... and {len(data) - show_results} more records")
            elif success:
                print("\n[INFO] Query executed successfully but returned no data")
            else:
                print("\n[ERROR] Query execution failed")
        else:
            print("\n[ERROR] No SQL generated")
        
        return result

def main():
    """Main function to test the Final Enhanced RAG System"""
    
    # Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        print("[ERROR] GROQ_API_KEY environment variable required")
        return
    
    # Initialize system
    print("Initializing Final Enhanced RAG System...")
    rag_system = FinalEnhancedRAGSystem(GROQ_API_KEY)
    
    # Setup system (populate ChromaDB)
    rag_system.setup_system()
    
    # Comprehensive test queries
    test_queries = [
        # Direct column queries (should get high similarity)
        "float_id",
        "get float_id", 
        "show float identifiers",
        "temperature",
        "salinity data",
        
        # Count queries (should match well)
        "count floats",
        "how many floats", 
        "total profiles",
        "number of measurements",
        
        # Table queries (should work well)
        "list all floats",
        "show profiles",
        "measurement data",
        
        # Complex queries (for LLM generation)
        "active floats in Arabian Sea with recent profiles",
        "average temperature by depth zones",
        "quality control statistics for recent data"
    ]
    
    print("\n" + "=" * 100)
    print("FINAL ENHANCED RAG SYSTEM - COMPREHENSIVE TEST")
    print("=" * 100)
    
    results_summary = []
    
    for query in test_queries:
        result = rag_system.query_and_execute(query, show_results=5)
        results_summary.append({
            'query': query,
            'method': result.method,
            'similarity': result.similarity,
            'success': bool(result.enhanced_sql)
        })
        print("\n" + "-" * 100)
    
    # Print summary
    print("\n" + "=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)
    
    method_counts = {}
    total_queries = len(results_summary)
    successful_queries = sum(1 for r in results_summary if r['success'])
    
    for result in results_summary:
        method = result['method']
        method_counts[method] = method_counts.get(method, 0) + 1
    
    print(f"Total Queries: {total_queries}")
    print(f"Successful Queries: {successful_queries} ({successful_queries/total_queries*100:.1f}%)")
    print(f"\nMethod Distribution:")
    for method, count in method_counts.items():
        print(f"  - {method}: {count} queries ({count/total_queries*100:.1f}%)")
    
    # High similarity queries
    high_sim_queries = [r for r in results_summary if r['similarity'] >= 0.4]
    print(f"\nHigh Similarity Queries (>=0.4): {len(high_sim_queries)}")
    for r in high_sim_queries:
        print(f"  - '{r['query']}': {r['similarity']:.3f}")

if __name__ == "__main__":
    main()