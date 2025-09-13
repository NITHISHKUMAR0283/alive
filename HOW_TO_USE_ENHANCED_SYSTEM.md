# How to Use the Enhanced RAG System

## 🚀 Quick Start

### Prerequisites
```bash
pip install chromadb groq sentence-transformers duckdb numpy
```

### API Keys Required
- **Groq API Key**: Get from https://console.groq.com/
- Update the API key in `working_enhanced_rag.py` line 563 and `interactive_test.py` line 11

### Usage
```bash
# Run the enhanced interactive system
python interactive_test.py

# Test individual profile queries (Option 2) - The enhanced feature!
# Show context-aware analysis (Option 6) - See how the system understands queries
```

## 🎯 Key Features

### ✅ Problem Solved: Semantic Similarity Precision
- **Before**: "temperature average for each profile" → Wrong geographic analysis
- **After**: "temperature average for each profile" → Correct individual profile analysis

### ✅ Enhanced Features
- **407 total queries** in ChromaDB (384 base + 23 enhanced)
- **Multi-stage semantic search** with intent classification
- **Context-aware similarity scoring** prevents semantic collisions
- **Individual profile analysis** for per-profile statistics
- **6 intent types**: individual_profile, geographic, global_aggregate, temporal, simple_retrieval, individual_float

### ✅ Query Types Supported
- **Individual Profile**: "temperature for each profile" → Profile-level statistics
- **Geographic**: "temperature by latitude" → Regional analysis  
- **Global Aggregate**: "average temperature overall" → Dataset-wide statistics
- **Simple Retrieval**: "show temperature data" → Raw data access

## 📊 System Performance

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

## 📋 Data Overview

**Oceanographic Dataset:**
- **17 ARGO floats** with deployment tracking
- **3,130 oceanographic profiles** with temporal/spatial context
- **1.4M quality-controlled measurements** (temperature, salinity, pressure)
- **Indian Ocean coverage** with comprehensive geographic distribution

## ⚠️ Known Issues

**ChromaDB Collection Creation:**
- The system may create new ChromaDB collection directories on some runs
- This is a ChromaDB behavior where delete/create cycles don't always clean up properly
- **Workaround**: The system reuses existing collections when possible
- **Impact**: Minimal - only affects disk space, not functionality

## 🤝 Contributing

This system was built with [Claude Code](https://claude.ai/code) for oceanographic data analysis and RAG system enhancement.