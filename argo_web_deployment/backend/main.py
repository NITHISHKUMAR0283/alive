#!/usr/bin/env python3
"""
FastAPI Backend for ARGO Oceanographic 3D Globe
Always-on backend with pagination and RAG integration
"""

import os
import sys
import json
import math
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from functools import lru_cache

import duckdb
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path to import existing RAG system
sys.path.append('../..')
# RAG system import
from working_enhanced_rag import WorkingRAGSystem

app = FastAPI(
    title="ARGO Oceanographic API",
    description="Always-on backend for 3D oceanographic data exploration",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with actual frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class FilterRequest(BaseModel):
    time_range: dict = None
    lat_range: list = None
    lon_range: list = None
    depth_range: list = None
    parameters: list = None
    deployment_year_range: list = None
    quality_levels: list = None
    network_types: list = None

class PaginationResponse(BaseModel):
    data: List[Dict]
    pagination: Dict[str, int]
    query_metadata: Dict[str, Any]

class FloatData(BaseModel):
    float_id: int
    latitude: float
    longitude: float
    profiles_count: int
    avg_temperature: Optional[float]
    deployment_date: Optional[str]

# Global variables for caching
query_cache = {}
connection_pool = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    global connection_pool
    
    print("Starting ARGO Oceanographic API...")
    
    # Initialize DuckDB connection
    connection_pool = duckdb.connect()
    
    # Load parquet data
    parquet_base_path = "parquet_data"
    if os.path.exists(f"{parquet_base_path}/measurements.parquet"):
        print("Loading parquet data into DuckDB...")
        # Global variables for caching
query_cache = {}
connection_pool = None
rag_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize database connections and RAG system on startup"""
    global connection_pool, rag_system
    
    print("Starting ARGO Oceanographic API...")
    
    # Initialize DuckDB connection
    connection_pool = duckdb.connect()
    
    # Load parquet data
    parquet_base_path = "parquet_data"
    if os.path.exists(f"{parquet_base_path}/measurements.parquet"):
        print("Loading parquet data into DuckDB...")
        connection_pool.execute(f"""
            CREATE OR REPLACE VIEW measurements AS 
            SELECT * FROM read_parquet('{parquet_base_path}/measurements.parquet')
        """)
        
        connection_pool.execute(f"""
            CREATE OR REPLACE VIEW profiles AS 
            SELECT * FROM read_parquet('{parquet_base_path}/profiles.parquet')
        """)
        
        connection_pool.execute(f"""
            CREATE OR REPLACE VIEW floats AS 
            SELECT * FROM read_parquet('{parquet_base_path}/floats.parquet')
        """)
        
        print("DuckDB initialized with oceanographic data")
    else:
        print("Parquet files not found - using mock data")
        
    # Initialize RAG system (disabled for now to get basic functionality working)
    print("[INFO] RAG system disabled for now - using keyword-based processing")
    rag_system = None
    
    print("ARGO API ready for 3D globe visualization!")

@app.get("/healthz")
async def health_check():
    """Health endpoint for UptimeRobot keep-alive"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "rag_loaded": rag_system is not None,
        "db_connected": connection_pool is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "ARGO Oceanographic API",
        "endpoints": {
            "health": "/healthz",
            "floats": "/api/floats-3d", 
            "query": "/api/query",
            "docs": "/docs"
        }
    }

def cached_rag_query(query_hash: str, query: str):
    """Cache RAG processing results"""
    return app.state.rag_system.process_query(query)

@app.get("/api/floats-3d")
async def get_floats_for_3d_globe():
    """Get float data optimized for 3D globe visualization"""
    try:
        if connection_pool is None:
            # Return mock data if no database
            return {
                "floats": [
                    {
                        "float_id": 7900635,
                        "latitude": -20.5,
                        "longitude": 85.2,
                        "profiles_count": 180,
                        "avg_temperature": 15.2,
                        "deployment_date": "2018-03-15"
                    },
                    {
                        "float_id": 7900636,
                        "latitude": -25.0,
                        "longitude": 80.0,
                        "profiles_count": 120,
                        "avg_temperature": 18.5,
                        "deployment_date": "2019-01-10"
                    }
                ]
            }
        
        # Query real data
        query = """
        SELECT 
            f.float_id,
            f.deployment_latitude as latitude,
            f.deployment_longitude as longitude,
            COUNT(p.profile_id) as profiles_count,
            AVG(m.temperature) as avg_temperature,
            f.deployment_date
        FROM floats f
        LEFT JOIN profiles p ON f.float_id = p.float_id
        LEFT JOIN measurements m ON p.profile_id = m.profile_id
        GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
        ORDER BY f.float_id
        """
        
        result = connection_pool.execute(query).fetchall()
        columns = [desc[0] for desc in connection_pool.description]
        
        floats_data = []
        for row in result:
            float_dict = dict(zip(columns, row))
            floats_data.append(float_dict)
        
        return {"floats": floats_data}
        
    except Exception as e:
        print(f"Error in floats-3d endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def process_query_with_pagination(
    request: QueryRequest,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=10, le=1000, description="Items per page")
):
    """
    Process natural language query with efficient pagination
    Handles large datasets without memory overflow
    """
    try:
        print(f"Processing query: {request.query}")
        
        if connection_pool is None:
            # Mock response if no database or RAG system
            return PaginationResponse(
                data=[
                    {"float_id": 7900635, "temperature": 15.2, "depth": 100.0},
                    {"float_id": 7900636, "temperature": 18.5, "depth": 150.0}
                ],
                pagination={
                    "total_records": 2,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                },
                query_metadata={
                    "intent": "mock_query",
                    "similarity": 1.0,
                    "method": "mock"
                }
            )
        
        # Process query with RAG if available, otherwise use simple processing
        if rag_system is not None:
            print("Using RAG system for query processing")
            rag_result = rag_system.process_query(request.query)
            base_sql = rag_result.enhanced_sql
            method = rag_result.method
            similarity = rag_result.similarity
            intent = rag_result.metadata.get('query_intent', {}).get('intent', 'unknown')
        else:
            print("RAG system not available, using simple keyword processing")
            # Fallback to simple keyword processing
            query_lower = request.query.lower()
            
            if any(word in query_lower for word in ['temperature', 'temp']):
                if 'average' in query_lower or 'avg' in query_lower:
                    base_sql = """
                    SELECT 
                        f.float_id,
                        f.deployment_latitude as latitude,
                        f.deployment_longitude as longitude,
                        COUNT(p.profile_id) as profiles_count,
                        AVG(m.temperature) as avg_temperature,
                        MIN(m.temperature) as min_temperature,
                        MAX(m.temperature) as max_temperature,
                        f.deployment_date
                    FROM floats f
                    LEFT JOIN profiles p ON f.float_id = p.float_id
                    LEFT JOIN measurements m ON p.profile_id = m.profile_id
                    WHERE m.temperature IS NOT NULL
                    GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
                    ORDER BY AVG(m.temperature) DESC
                    """
                else:
                    base_sql = """
                    SELECT 
                        f.float_id,
                        f.deployment_latitude as latitude,
                        f.deployment_longitude as longitude,
                        m.temperature,
                        m.pressure as depth,
                        p.profile_date,
                        f.deployment_date
                    FROM floats f
                    LEFT JOIN profiles p ON f.float_id = p.float_id
                    LEFT JOIN measurements m ON p.profile_id = m.profile_id
                    WHERE m.temperature IS NOT NULL
                    ORDER BY m.temperature DESC
                    LIMIT 1000
                    """
            elif any(word in query_lower for word in ['salinity', 'salt']):
                base_sql = """
                SELECT 
                    f.float_id,
                    f.deployment_latitude as latitude,
                    f.deployment_longitude as longitude,
                    m.salinity,
                    m.pressure as depth,
                    p.profile_date,
                    f.deployment_date
                FROM floats f
                LEFT JOIN profiles p ON f.float_id = p.float_id
                LEFT JOIN measurements m ON p.profile_id = m.profile_id
                WHERE m.salinity IS NOT NULL
                ORDER BY m.salinity DESC
                LIMIT 1000
                """
            else:
                # Default query for general data exploration
                base_sql = """
                SELECT 
                    f.float_id,
                    f.deployment_latitude as latitude,
                    f.deployment_longitude as longitude,
                    COUNT(p.profile_id) as profiles_count,
                    AVG(m.temperature) as avg_temperature,
                    AVG(m.salinity) as avg_salinity,
                    f.deployment_date
                FROM floats f
                LEFT JOIN profiles p ON f.float_id = p.float_id
                LEFT JOIN measurements m ON p.profile_id = m.profile_id
                GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
                ORDER BY f.float_id
                """
            method = "keyword_based_sql"
            similarity = 1.0
            intent = "basic_query"
        
        if not base_sql:
            raise HTTPException(status_code=400, detail="Could not generate SQL for the query.")
        
        # Get total count - handle LIMIT in subqueries
        if "LIMIT" in base_sql.upper():
            # For queries with LIMIT, execute the query first to get actual count
            try:
                result = connection_pool.execute(base_sql).fetchall()
                total_records = len(result)
            except:
                # If that fails, try to remove LIMIT for counting
                count_sql = base_sql.split("LIMIT")[0].strip()
                total_records = connection_pool.execute(f"SELECT COUNT(*) FROM ({count_sql})").fetchone()[0]
        else:
            count_sql = f"SELECT COUNT(*) FROM ({base_sql})"
            total_records = connection_pool.execute(count_sql).fetchone()[0]
        
        # Calculate pagination
        total_pages = math.ceil(total_records / page_size)
        offset = (page - 1) * page_size
        
        # Execute paginated query
        paginated_sql = f"{base_sql} LIMIT {page_size} OFFSET {offset}"
        result = connection_pool.execute(paginated_sql).fetchall()
        columns = [desc[0] for desc in connection_pool.description]
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in result]
        
        return PaginationResponse(
            data=data,
            pagination={
                "total_records": total_records,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            query_metadata={
                "intent": intent,
                "similarity": similarity,
                "method": method,
                "sql_preview": base_sql[:200] + "..." if len(base_sql) > 200 else base_sql
            }
        )
        
    except Exception as e:
        print(f"Error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
async def health_check():
    """Health endpoint for UptimeRobot keep-alive"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "rag_loaded": rag_system is not None,
        "db_connected": connection_pool is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "ARGO Oceanographic API",
        "endpoints": {
            "health": "/healthz",
            "floats": "/api/floats-3d", 
            "query": "/api/query",
            "docs": "/docs"
        }
    }

# RAG system disabled for now
# @lru_cache(maxsize=50)
# def cached_rag_query(query_hash: str, query: str):
#     """Cache RAG processing results"""
#     return app.state.rag_system.process_query(query)

@app.get("/api/floats-3d")
async def get_floats_for_3d_globe():
    """Get float data optimized for 3D globe visualization"""
    try:
        if connection_pool is None:
            # Return mock data if no database
            return {
                "floats": [
                    {
                        "float_id": 7900635,
                        "latitude": -20.5,
                        "longitude": 85.2,
                        "profiles_count": 180,
                        "avg_temperature": 15.2,
                        "deployment_date": "2018-03-15"
                    },
                    {
                        "float_id": 7900636,
                        "latitude": -25.0,
                        "longitude": 80.0,
                        "profiles_count": 120,
                        "avg_temperature": 18.5,
                        "deployment_date": "2019-01-10"
                    }
                ]
            }
        
        # Query real data
        query = """
        SELECT 
            f.float_id,
            f.deployment_latitude as latitude,
            f.deployment_longitude as longitude,
            COUNT(p.profile_id) as profiles_count,
            AVG(m.temperature) as avg_temperature,
            f.deployment_date
        FROM floats f
        LEFT JOIN profiles p ON f.float_id = p.float_id
        LEFT JOIN measurements m ON p.profile_id = m.profile_id
        GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
        ORDER BY f.float_id
        """
        
        result = connection_pool.execute(query).fetchall()
        columns = [desc[0] for desc in connection_pool.description]
        
        floats_data = []
        for row in result:
            float_dict = dict(zip(columns, row))
            floats_data.append(float_dict)
        
        return {"floats": floats_data}
        
    except Exception as e:
        print(f"Error in floats-3d endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def process_query_with_pagination(
    request: QueryRequest,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=10, le=1000, description="Items per page")
):
    """
    Process natural language query with efficient pagination
    Handles large datasets without memory overflow
    """
    try:
        print(f"Processing query: {request.query}")
        
        if connection_pool is None:
            # Mock response if no database
            return PaginationResponse(
                data=[
                    {"float_id": 7900635, "temperature": 15.2, "depth": 100.0},
                    {"float_id": 7900636, "temperature": 18.5, "depth": 150.0}
                ],
                pagination={
                    "total_records": 2,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                },
                query_metadata={
                    "intent": "mock_query",
                    "similarity": 1.0,
                    "method": "mock"
                }
            )
        
        # Process natural language query and generate appropriate SQL
        query_lower = request.query.lower()
        
        # Basic query processing based on keywords
        if any(word in query_lower for word in ['temperature', 'temp']):
            if 'average' in query_lower or 'avg' in query_lower:
                base_sql = """
                SELECT 
                    f.float_id,
                    f.deployment_latitude as latitude,
                    f.deployment_longitude as longitude,
                    COUNT(p.profile_id) as profiles_count,
                    AVG(m.temperature) as avg_temperature,
                    MIN(m.temperature) as min_temperature,
                    MAX(m.temperature) as max_temperature,
                    f.deployment_date
                FROM floats f
                LEFT JOIN profiles p ON f.float_id = p.float_id
                LEFT JOIN measurements m ON p.profile_id = m.profile_id
                WHERE m.temperature IS NOT NULL
                GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
                ORDER BY AVG(m.temperature) DESC
                """
            else:
                base_sql = """
                SELECT 
                    f.float_id,
                    f.deployment_latitude as latitude,
                    f.deployment_longitude as longitude,
                    m.temperature,
                    m.pressure as depth,
                    p.profile_date,
                    f.deployment_date
                FROM floats f
                LEFT JOIN profiles p ON f.float_id = p.float_id
                LEFT JOIN measurements m ON p.profile_id = m.profile_id
                WHERE m.temperature IS NOT NULL
                ORDER BY m.temperature DESC
                LIMIT 1000
                """
        elif any(word in query_lower for word in ['salinity', 'salt']):
            base_sql = """
            SELECT 
                f.float_id,
                f.deployment_latitude as latitude,
                f.deployment_longitude as longitude,
                m.salinity,
                m.pressure as depth,
                p.profile_date,
                f.deployment_date
            FROM floats f
            LEFT JOIN profiles p ON f.float_id = p.float_id
            LEFT JOIN measurements m ON p.profile_id = m.profile_id
            WHERE m.salinity IS NOT NULL
            ORDER BY m.salinity DESC
            LIMIT 1000
            """
        elif any(word in query_lower for word in ['depth', 'pressure']):
            base_sql = """
            SELECT 
                f.float_id,
                f.deployment_latitude as latitude,
                f.deployment_longitude as longitude,
                m.pressure as depth,
                m.temperature,
                m.salinity,
                p.profile_date,
                f.deployment_date
            FROM floats f
            LEFT JOIN profiles p ON f.float_id = p.float_id
            LEFT JOIN measurements m ON p.profile_id = m.profile_id
            WHERE m.pressure IS NOT NULL
            ORDER BY m.pressure DESC
            LIMIT 1000
            """
        elif any(word in query_lower for word in ['float', 'floats', 'list', 'show']):
            base_sql = """
            SELECT 
                f.float_id,
                f.deployment_latitude as latitude,
                f.deployment_longitude as longitude,
                COUNT(p.profile_id) as profiles_count,
                AVG(m.temperature) as avg_temperature,
                f.deployment_date
            FROM floats f
            LEFT JOIN profiles p ON f.float_id = p.float_id
            LEFT JOIN measurements m ON p.profile_id = m.profile_id
            GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
            ORDER BY f.float_id
            """
        else:
            # Default query for general data exploration
            base_sql = """
            SELECT 
                f.float_id,
                f.deployment_latitude as latitude,
                f.deployment_longitude as longitude,
                COUNT(p.profile_id) as profiles_count,
                AVG(m.temperature) as avg_temperature,
                AVG(m.salinity) as avg_salinity,
                f.deployment_date
            FROM floats f
            LEFT JOIN profiles p ON f.float_id = p.float_id
            LEFT JOIN measurements m ON p.profile_id = m.profile_id
            GROUP BY f.float_id, f.deployment_latitude, f.deployment_longitude, f.deployment_date
            ORDER BY f.float_id
            """
        
        # Get total count
        count_sql = f"SELECT COUNT(*) FROM ({base_sql})"
        total_records = connection_pool.execute(count_sql).fetchone()[0]
        
        # Calculate pagination
        total_pages = math.ceil(total_records / page_size)
        offset = (page - 1) * page_size
        
        # Execute paginated query
        paginated_sql = f"{base_sql} LIMIT {page_size} OFFSET {offset}"
        result = connection_pool.execute(paginated_sql).fetchall()
        columns = [desc[0] for desc in connection_pool.description]
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in result]
        
        return PaginationResponse(
            data=data,
            pagination={
                "total_records": total_records,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            query_metadata={
                "intent": "processed_query",
                "similarity": 1.0,
                "method": "keyword_based_sql",
                "original_query": request.query,
                "sql_preview": base_sql[:200] + "..." if len(base_sql) > 200 else base_sql
            }
        )
        
    except Exception as e:
        print(f"Error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/filter-options")
async def get_filter_options():
    """Get available filter options from the database"""
    try:
        if connection_pool is None:
            # Mock filter options
            return {
                "parameters": ["temperature", "salinity", "pressure"],
                "qualityLevels": ["good", "probably_good", "bad"],
                "networks": ["ARGO", "CORE-ARGO", "BGC-ARGO"],
                "dateRange": {"min": "2000-01-01", "max": "2024-12-31"},
                "depthRange": {"min": 0, "max": 2000},
                "geoRange": {"latMin": -80, "latMax": 80, "lonMin": -180, "lonMax": 180}
            }
        
        # Get actual data ranges from database
        options = {}
        
        # Available parameters - DuckDB compatible query
        try:
            # Check if measurements table exists and has expected columns
            table_info = connection_pool.execute("DESCRIBE measurements").fetchall()
            available_columns = [row[0] for row in table_info]
            param_columns = [col for col in ['temperature', 'salinity', 'pressure'] if col in available_columns]
            options["parameters"] = param_columns if param_columns else ["temperature", "salinity", "pressure"]
        except:
            options["parameters"] = ["temperature", "salinity", "pressure"]
        
        # Quality levels
        try:
            quality_query = "SELECT DISTINCT temperature_qc FROM measurements WHERE temperature_qc IS NOT NULL LIMIT 10"
            quality_levels = connection_pool.execute(quality_query).fetchall()
            options["qualityLevels"] = [str(q[0]) for q in quality_levels]
        except:
            options["qualityLevels"] = ["1", "2", "3", "4"]
        
        # Network types
        try:
            network_query = "SELECT DISTINCT program_name FROM floats WHERE program_name IS NOT NULL LIMIT 20"
            networks = connection_pool.execute(network_query).fetchall()
            options["networks"] = [n[0] for n in networks if n[0]]
        except:
            options["networks"] = ["ARGO", "CORE-ARGO"]
        
        # Date range - try different column names
        try:
            # Try different possible date column names
            date_columns = ['date', 'profile_date', 'deployment_date']
            date_range = None
            for col in date_columns:
                try:
                    date_query = f"SELECT MIN({col}), MAX({col}) FROM profiles WHERE {col} IS NOT NULL"
                    date_range = connection_pool.execute(date_query).fetchone()
                    if date_range and date_range[0]:
                        break
                except:
                    continue
            
            if date_range and date_range[0]:
                options["dateRange"] = {
                    "min": str(date_range[0]),
                    "max": str(date_range[1])
                }
            else:
                options["dateRange"] = {"min": "2000-01-01", "max": "2024-12-31"}
        except:
            options["dateRange"] = {"min": "2000-01-01", "max": "2024-12-31"}
        
        # Depth range
        try:
            depth_query = "SELECT MIN(pressure), MAX(pressure) FROM measurements WHERE pressure IS NOT NULL"
            depth_range = connection_pool.execute(depth_query).fetchone()
            options["depthRange"] = {
                "min": int(depth_range[0]) if depth_range[0] else 0,
                "max": int(depth_range[1]) if depth_range[1] else 2000
            }
        except:
            options["depthRange"] = {"min": 0, "max": 2000}
        
        # Geographic range - try different column names
        try:
            # Try different possible coordinate column names
            lat_columns = ['deployment_latitude', 'latitude', 'lat']
            lon_columns = ['deployment_longitude', 'longitude', 'lon']
            geo_range = None
            
            for lat_col in lat_columns:
                for lon_col in lon_columns:
                    try:
                        geo_query = f"SELECT MIN({lat_col}), MAX({lat_col}), MIN({lon_col}), MAX({lon_col}) FROM floats WHERE {lat_col} IS NOT NULL"
                        geo_range = connection_pool.execute(geo_query).fetchone()
                        if geo_range and geo_range[0] is not None:
                            break
                    except:
                        continue
                if geo_range and geo_range[0] is not None:
                    break
            
            if geo_range and geo_range[0] is not None:
                options["geoRange"] = {
                    "latMin": float(geo_range[0]),
                    "latMax": float(geo_range[1]),
                    "lonMin": float(geo_range[2]),
                    "lonMax": float(geo_range[3])
                }
            else:
                options["geoRange"] = {"latMin": -80, "latMax": 80, "lonMin": -180, "lonMax": 180}
        except:
            options["geoRange"] = {"latMin": -80, "latMax": 80, "lonMin": -180, "lonMax": 180}
        
        return options
        
    except Exception as e:
        print(f"Error in filter-options endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/filtered-data")
async def get_filtered_data(
    filters: FilterRequest,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=10, le=1000, description="Items per page")
):
    """Get filtered oceanographic data based on user criteria"""
    try:
        if connection_pool is None:
            # Mock filtered response
            return PaginationResponse(
                data=[
                    {"float_id": 7900635, "temperature": 15.2, "depth": 100.0, "date": "2023-01-15"},
                    {"float_id": 7900636, "temperature": 18.5, "depth": 150.0, "date": "2023-02-20"}
                ],
                pagination={
                    "total_records": 2,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                },
                query_metadata={
                    "filters_applied": filters.dict(),
                    "method": "filtered_data"
                }
            )
        
        # Build dynamic SQL with filters - using correct column names
        base_query = """
        SELECT 
            m.profile_id,
            f.float_id,
            m.temperature,
            m.salinity,
            m.pressure,
            p.profile_date as date,
            f.deployment_latitude as latitude,
            f.deployment_longitude as longitude
        FROM measurements m
        JOIN profiles p ON m.profile_id = p.profile_id
        JOIN floats f ON p.float_id = f.float_id
        WHERE 1=1
        """
        
        where_conditions = []
        
        # Apply filters
        if filters.lat_range:
            where_conditions.append(f"f.deployment_latitude BETWEEN {filters.lat_range[0]} AND {filters.lat_range[1]}")
        
        if filters.lon_range:
            where_conditions.append(f"f.deployment_longitude BETWEEN {filters.lon_range[0]} AND {filters.lon_range[1]}")
        
        if filters.depth_range:
            where_conditions.append(f"m.pressure BETWEEN {filters.depth_range[0]} AND {filters.depth_range[1]}")
        
        if filters.time_range and filters.time_range.get('startDate'):
            where_conditions.append(f"p.profile_date >= '{filters.time_range['startDate']}'")
        
        if filters.time_range and filters.time_range.get('endDate'):
            where_conditions.append(f"p.profile_date <= '{filters.time_range['endDate']}'")
        
        if filters.parameters:
            # Only include requested parameters in SELECT
            param_columns = [p for p in filters.parameters if p in ['temperature', 'salinity', 'pressure']]
            if param_columns:
                # Add quality filters for selected parameters
                for param in param_columns:
                    if param == 'temperature':
                        where_conditions.append("m.temperature_qc <= 2")
                    elif param == 'salinity':
                        where_conditions.append("m.salinity_qc <= 2")
        
        if filters.quality_levels:
            quality_conditions = []
            for level in filters.quality_levels:
                quality_conditions.append(f"m.temperature_qc = {level}")
            if quality_conditions:
                where_conditions.append(f"({' OR '.join(quality_conditions)})")
        
        if filters.network_types:
            network_conditions = []
            for network in filters.network_types:
                network_conditions.append(f"f.program_name = '{network}'")
            if network_conditions:
                where_conditions.append(f"({' OR '.join(network_conditions)})")
        
        if filters.deployment_year_range:
            where_conditions.append(f"EXTRACT(year FROM f.deployment_date::date) BETWEEN {filters.deployment_year_range[0]} AND {filters.deployment_year_range[1]}")
        
        # Combine query with filters
        if where_conditions:
            filtered_query = base_query + " AND " + " AND ".join(where_conditions)
        else:
            filtered_query = base_query
        
        # Get total count
        count_sql = f"SELECT COUNT(*) FROM ({filtered_query})"
        total_records = connection_pool.execute(count_sql).fetchone()[0]
        
        # Apply pagination
        total_pages = math.ceil(total_records / page_size)
        offset = (page - 1) * page_size
        paginated_sql = f"{filtered_query} LIMIT {page_size} OFFSET {offset}"
        
        # Execute query
        result = connection_pool.execute(paginated_sql).fetchall()
        columns = [desc[0] for desc in connection_pool.description]
        
        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in result]
        
        return PaginationResponse(
            data=data,
            pagination={
                "total_records": total_records,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            query_metadata={
                "filters_applied": filters.dict(),
                "method": "filtered_data",
                "sql_preview": paginated_sql[:200] + "..." if len(paginated_sql) > 200 else paginated_sql
            }
        )
        
    except Exception as e:
        print(f"Error in filtered-data endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working",
        "rag_available": False,  # RAG system disabled for now
        "db_available": connection_pool is not None
    }

