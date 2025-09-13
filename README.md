# Enhanced RAG System for Oceanographic Data Analysis

## 🎯 Context-Aware RAG with Individual Profile Analysis

✅ **Problem Solved: Semantic Similarity Precision**
- **Before**: "temperature average for each profile" → Wrong geographic analysis
- **After**: "temperature average for each profile" → Correct individual profile analysis

✅ **Enhanced Features:**
- **407 total queries** in ChromaDB (384 base + 23 enhanced)
- **Multi-stage semantic search** with intent classification
- **Context-aware similarity scoring** prevents semantic collisions
- **Individual profile analysis** for per-profile statistics
- **6 intent types**: individual_profile, geographic, global_aggregate, temporal, simple_retrieval, individual_float

## 🚀 Quick Start

```bash
# Run the enhanced interactive system
python interactive_test.py

# Test individual profile queries (Option 2)
# Show context-aware analysis (Option 6)
```

## 📊 System Performance

**Query Types Supported:**
- **Individual Profile**: "temperature for each profile" → Profile-level statistics
- **Geographic**: "temperature by latitude" → Regional analysis  
- **Global Aggregate**: "average temperature overall" → Dataset-wide statistics
- **Simple Retrieval**: "show temperature data" → Raw data access

**Technical Improvements:**
- **Intent Detection**: Classifies query purpose automatically
- **Grouping Level Matching**: 1.3x bonus for correct grouping, 0.6x penalty for wrong grouping
- **Context Scoring**: Prevents matching wrong query types
- **Precision Matching**: No more semantic collisions

## 🔧 Technical Stack

- **ChromaDB**: 407-query vector database with context metadata
- **Multi-stage Search**: Intent → Semantic → Context → Ranking
- **DuckDB**: Efficient querying of 1.4M oceanographic measurements
- **Groq LLM**: Dynamic SQL generation with context awareness
- **Fast Embeddings**: all-MiniLM-L6-v2 for local processing

## 📁 Repository Structure

**Core System Files:**
```
working_enhanced_rag.py           # Enhanced RAG system with context-aware search
optimized_chromadb_data.json     # 407 queries with individual profile analysis
interactive_test.py               # Enhanced user interface
parquet_data/                     # Oceanographic data (floats, profiles, measurements)
working_enhanced_chroma_db/       # Vector database with embeddings
```

**Documentation:**
```
README.md                         # This file
HOW_TO_USE_ENHANCED_SYSTEM.md    # Detailed usage instructions
```

**Development & Backup Files:**
```
deployments/                      # Backup files, development scripts, and testing tools
├── backup_rag_system.py         # Backup version of RAG system
├── backup_chroma_db/             # Backup ChromaDB
├── apply_enhanced_system.py     # Deployment script
├── test_critical_query.py       # Specific query test
└── fix.md                        # Technical implementation guide
```

## 📋 Data Overview

**Oceanographic Dataset:**
- **17 ARGO floats** with deployment tracking
- **3,130 oceanographic profiles** with temporal/spatial context
- **1.4M quality-controlled measurements** (temperature, salinity, pressure)
- **Indian Ocean coverage** with comprehensive geographic distribution

🚀 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
