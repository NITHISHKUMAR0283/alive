#!/usr/bin/env python3
"""
Analyze Parquet files to create optimized ChromaDB data with real schema information
"""

import os
import json
import duckdb
import pandas as pd
from typing import Dict, List, Any

def analyze_parquet_schema(parquet_path: str = "./parquet_data") -> Dict[str, Any]:
    """Analyze parquet files to understand the real database schema"""
    
    conn = duckdb.connect()
    schema_info = {}
    
    parquet_files = {
        'floats': f"{parquet_path}/floats.parquet",
        'profiles': f"{parquet_path}/profiles.parquet",
        'measurements': f"{parquet_path}/measurements.parquet",
        'spatial_summaries': f"{parquet_path}/spatial_summaries.parquet",
        'quality_control_tests': f"{parquet_path}/quality_control_tests.parquet",
        'quality_control_results': f"{parquet_path}/quality_control_results.parquet"
    }
    
    for table_name, file_path in parquet_files.items():
        if os.path.exists(file_path):
            print(f"[INFO] Analyzing {table_name}...")
            
            try:
                # Load parquet and get schema
                df = pd.read_parquet(file_path)
                
                # Get column information
                columns = []
                for col in df.columns:
                    col_info = {
                        'name': col,
                        'dtype': str(df[col].dtype),
                        'null_count': df[col].isnull().sum(),
                        'unique_values': df[col].nunique() if df[col].nunique() < 20 else None
                    }
                    
                    # Get sample values for small cardinality columns
                    if df[col].nunique() < 20 and df[col].dtype == 'object':
                        col_info['sample_values'] = df[col].dropna().unique().tolist()[:10]
                    elif df[col].dtype in ['float64', 'int64']:
                        col_info['min_value'] = df[col].min() if not pd.isna(df[col].min()) else None
                        col_info['max_value'] = df[col].max() if not pd.isna(df[col].max()) else None
                    
                    columns.append(col_info)
                
                schema_info[table_name] = {
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'columns': columns,
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
                
                print(f"  - {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                print(f"  - ERROR: {e}")
                schema_info[table_name] = {'error': str(e)}
    
    return schema_info

def create_optimized_chromadb_data(schema_info: Dict[str, Any]) -> List[Dict]:
    """Create optimized ChromaDB data using real schema information"""
    
    optimized_queries = []
    query_id = 1
    
    # 1. DIRECT COLUMN QUERIES - Based on actual schema
    for table_name, table_info in schema_info.items():
        if 'columns' not in table_info:
            continue
            
        for col in table_info['columns']:
            col_name = col['name']
            
            # Create direct column access queries
            queries = [
                {
                    'content': f"get {col_name}",
                    'sql': f"SELECT {col_name} FROM {table_name}",
                    'intent': f"retrieve {col_name} values from {table_name}",
                    'context': f"Direct access to {col_name} column in {table_name} table"
                },
                {
                    'content': f"show {col_name}",
                    'sql': f"SELECT {col_name} FROM {table_name} LIMIT 100",
                    'intent': f"display {col_name} data from {table_name}",
                    'context': f"Limited view of {col_name} column data"
                },
                {
                    'content': f"list {col_name}",
                    'sql': f"SELECT DISTINCT {col_name} FROM {table_name}",
                    'intent': f"list unique {col_name} values",
                    'context': f"Unique values in {col_name} column"
                }
            ]
            
            for query in queries:
                enhanced_content = f"""
                Column Query: {query['content']}
                Intent: {query['intent']}
                Context: {query['context']}
                Table: {table_name}
                Column: {col_name}
                Data Type: {col['dtype']}
                SQL: {query['sql']}
                Usage: Direct column access for data extraction
                """
                
                optimized_queries.append({
                    'id': f"col_{query_id:04d}",
                    'content': enhanced_content.strip(),
                    'metadata': {
                        'type': 'column_query',
                        'table': table_name,
                        'column': col_name,
                        'category': 'direct_access',
                        'complexity': 'simple',
                        'data_type': col['dtype']
                    }
                })
                query_id += 1
    
    # 2. TABLE-SPECIFIC QUERIES - Based on actual table structure
    
    # FLOATS table queries
    if 'floats' in schema_info:
        float_queries = [
            {
                'content': "all floats",
                'sql': "SELECT * FROM floats",
                'intent': "retrieve all float records",
                'variations': ["show all floats", "get floats", "list floats", "float data"]
            },
            {
                'content': "float identifiers", 
                'sql': "SELECT float_id FROM floats",
                'intent': "get float identification numbers",
                'variations': ["float id", "float ids", "show float id", "get float identifiers"]
            },
            {
                'content': "active floats",
                'sql': "SELECT * FROM floats WHERE current_status = 'ACTIVE'",
                'intent': "retrieve operational floats",
                'variations': ["operational floats", "working floats", "live floats"]
            }
        ]
        
        for query in float_queries:
            for variation in [query['content']] + query.get('variations', []):
                enhanced_content = f"""
                Float Query: {variation}
                Intent: {query['intent']}
                Table: floats
                SQL: {query['sql']}
                Context: ARGO float database query for float information
                Usage: Extract float data from the floats table
                Related Columns: {', '.join([col['name'] for col in schema_info['floats']['columns']])}
                """
                
                optimized_queries.append({
                    'id': f"float_{query_id:04d}",
                    'content': enhanced_content.strip(),
                    'metadata': {
                        'type': 'table_query',
                        'table': 'floats',
                        'category': 'float_operations',
                        'complexity': 'simple',
                        'intent': query['intent']
                    }
                })
                query_id += 1
    
    # MEASUREMENTS table queries - High priority for oceanographic data
    if 'measurements' in schema_info:
        measurement_queries = [
            {
                'content': "temperature data",
                'sql': "SELECT temperature FROM measurements WHERE temperature_qc <= 2",
                'intent': "retrieve quality temperature measurements",
                'variations': ["temp data", "temperature values", "get temperature", "show temperature"]
            },
            {
                'content': "salinity data", 
                'sql': "SELECT salinity FROM measurements WHERE salinity_qc <= 2",
                'intent': "retrieve quality salinity measurements", 
                'variations': ["sal data", "salinity values", "get salinity", "show salinity"]
            },
            {
                'content': "pressure data",
                'sql': "SELECT pressure FROM measurements",
                'intent': "retrieve pressure measurements",
                'variations': ["pressure values", "get pressure", "show pressure", "depth data"]
            },
            {
                'content': "measurement data",
                'sql': "SELECT pressure, temperature, salinity FROM measurements WHERE temperature_qc <= 2 AND salinity_qc <= 2",
                'intent': "retrieve quality oceanographic measurements",
                'variations': ["measurements", "ocean data", "sensor data", "CTD data"]
            }
        ]
        
        for query in measurement_queries:
            for variation in [query['content']] + query.get('variations', []):
                enhanced_content = f"""
                Measurement Query: {variation}
                Intent: {query['intent']}
                Table: measurements
                SQL: {query['sql']}
                Context: Oceanographic measurement data from ARGO CTD sensors
                Usage: Extract oceanographic parameters (temperature, salinity, pressure)
                Quality Control: Includes quality flags for data reliability
                Related Columns: {', '.join([col['name'] for col in schema_info['measurements']['columns']])}
                """
                
                optimized_queries.append({
                    'id': f"meas_{query_id:04d}",
                    'content': enhanced_content.strip(),
                    'metadata': {
                        'type': 'measurement_query',
                        'table': 'measurements',
                        'category': 'oceanographic_data',
                        'complexity': 'simple',
                        'intent': query['intent']
                    }
                })
                query_id += 1
    
    # 3. COUNT/STATISTICS QUERIES - Based on actual tables
    for table_name in schema_info.keys():
        if 'columns' not in schema_info[table_name]:
            continue
            
        count_queries = [
            {
                'content': f"count {table_name}",
                'sql': f"SELECT COUNT(*) FROM {table_name}",
                'intent': f"count total {table_name} records",
                'variations': [f"how many {table_name}", f"total {table_name}", f"number of {table_name}"]
            }
        ]
        
        for query in count_queries:
            for variation in [query['content']] + query.get('variations', []):
                enhanced_content = f"""
                Count Query: {variation}
                Intent: {query['intent']}
                Table: {table_name}
                SQL: {query['sql']}
                Context: Statistical count of records in {table_name} table
                Usage: Get total record count for {table_name}
                Total Records: {schema_info[table_name].get('row_count', 'unknown')}
                """
                
                optimized_queries.append({
                    'id': f"count_{query_id:04d}",
                    'content': enhanced_content.strip(),
                    'metadata': {
                        'type': 'count_query',
                        'table': table_name,
                        'category': 'statistics',
                        'complexity': 'simple',
                        'intent': query['intent']
                    }
                })
                query_id += 1
    
    # 4. JOIN QUERIES - Based on relationships
    join_queries = [
        {
            'content': "float profiles",
            'sql': "SELECT f.float_id, f.wmo_number, p.profile_id, p.profile_date FROM floats f JOIN profiles p ON f.float_id = p.float_id",
            'intent': "retrieve float profile relationships",
            'variations': ["profiles for floats", "float profile data", "linked profiles"]
        },
        {
            'content': "profile measurements", 
            'sql': "SELECT p.profile_id, p.profile_date, m.pressure, m.temperature, m.salinity FROM profiles p JOIN measurements m ON p.profile_id = m.profile_id WHERE m.temperature_qc <= 2",
            'intent': "retrieve profile measurement data",
            'variations': ["measurements for profiles", "profile data", "oceanographic profiles"]
        }
    ]
    
    for query in join_queries:
        for variation in [query['content']] + query.get('variations', []):
            enhanced_content = f"""
            Join Query: {variation}
            Intent: {query['intent']}
            Tables: Multiple tables with relationships
            SQL: {query['sql']}
            Context: Relational query combining data from linked tables
            Usage: Extract related data across table relationships
            """
            
            optimized_queries.append({
                'id': f"join_{query_id:04d}",
                'content': enhanced_content.strip(),
                'metadata': {
                    'type': 'join_query',
                    'category': 'relational',
                    'complexity': 'medium',
                    'intent': query['intent']
                }
            })
            query_id += 1
    
    print(f"[SUCCESS] Created {len(optimized_queries)} optimized queries")
    return optimized_queries

def main():
    """Main function to analyze schema and create optimized ChromaDB data"""
    
    print("=" * 80)
    print("PARQUET SCHEMA ANALYSIS & CHROMADB OPTIMIZATION")
    print("=" * 80)
    
    # Analyze parquet schema
    schema_info = analyze_parquet_schema()
    
    # Save schema analysis
    with open('parquet_schema_analysis.json', 'w') as f:
        json.dump(schema_info, f, indent=2, default=str)
    print(f"\n[SUCCESS] Schema analysis saved to parquet_schema_analysis.json")
    
    # Create optimized ChromaDB data
    optimized_data = create_optimized_chromadb_data(schema_info)
    
    # Save optimized ChromaDB data
    optimized_export = {
        'collection_info': {
            'name': 'optimized_argo_queries',
            'description': 'Schema-optimized ARGO queries for maximum semantic similarity',
            'total_documents': len(optimized_data),
            'optimization_features': [
                'Real schema column integration',
                'Multiple query variations',
                'Semantic enrichment with context',
                'Table relationship awareness',
                'Quality control integration'
            ]
        },
        'schema_info': schema_info,
        'queries': optimized_data,
        'summary': {
            'total_queries': len(optimized_data),
            'query_types': list(set([q['metadata']['type'] for q in optimized_data])),
            'tables_covered': list(set([q['metadata'].get('table', 'unknown') for q in optimized_data])),
            'categories': list(set([q['metadata']['category'] for q in optimized_data]))
        }
    }
    
    with open('optimized_chromadb_data.json', 'w') as f:
        json.dump(optimized_export, f, indent=2, default=str)
    
    print(f"[SUCCESS] Optimized ChromaDB data saved to optimized_chromadb_data.json")
    print(f"[INFO] Total optimized queries: {len(optimized_data)}")
    
    # Display summary
    print("\n" + "=" * 50)
    print("OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    print(f"Total Tables Analyzed: {len(schema_info)}")
    for table_name, info in schema_info.items():
        if 'row_count' in info:
            print(f"  - {table_name}: {info['row_count']} rows, {info['column_count']} columns")
    
    print(f"\nTotal Optimized Queries: {len(optimized_data)}")
    query_types = {}
    for query in optimized_data:
        qtype = query['metadata']['type']
        query_types[qtype] = query_types.get(qtype, 0) + 1
    
    for qtype, count in query_types.items():
        print(f"  - {qtype}: {count} queries")

if __name__ == "__main__":
    main()