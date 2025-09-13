#!/usr/bin/env python3
"""
Interactive RAG Testing Script
Run this to test queries interactively with the enhanced RAG system
"""

from working_enhanced_rag import WorkingRAGSystem

def main():
    # Initialize system
    GROQ_API_KEY = "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"
    
    print("Initializing Enhanced RAG System...")
    rag_system = WorkingRAGSystem(GROQ_API_KEY)
    
    # Check if ChromaDB needs setup
    try:
        current_count = rag_system.chroma_manager.collection.count()
        if current_count > 0:
            print(f"[INFO] Using existing ChromaDB with {current_count} queries")
        else:
            print("[INFO] ChromaDB is empty - setting up...")
            rag_system.setup_system()
    except Exception as e:
        print(f"[INFO] Setting up ChromaDB: {e}")
        rag_system.setup_system()
    
    print("\n" + "="*60)
    print("ENHANCED INTERACTIVE RAG TESTING")
    print("="*60)
    print("Features: Context-Aware Search | Intent Detection | Individual Profile Analysis")
    print("Total queries in ChromaDB: 407 (with individual profile analysis)")
    
    while True:
        print("\nOptions:")
        print("1. Test a custom query")
        print("2. Test INDIVIDUAL PROFILE queries (Enhanced!)")
        print("3. Test temperature average query")
        print("4. Test temperature depth distribution")
        print("5. Test all temperature queries")
        print("6. Show context-aware analysis for a query")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            query = input("Enter your query: ").strip()
            if query:
                print(f"\nTesting: {query}")
                print("-" * 40)
                rag_system.test_and_execute(query, show_results=3)
        
        elif choice == '2':
            print("\nTesting INDIVIDUAL PROFILE Queries (Enhanced Feature!)")
            print("-" * 50)
            print("These queries were failing before but now work correctly:")
            queries = [
                "give me temperature average for each profile",
                "temperature per profile", 
                "individual profile temperature statistics",
                "salinity average for each profile",
                "temperature data for each profile"
            ]
            for q in queries:
                print(f"\nQuery: {q}")
                result = rag_system.process_query(q)
                intent_info = result.metadata.get('query_intent', {})
                print(f"Intent: {intent_info.get('intent')}, Grouping: {intent_info.get('grouping_level')}")
                print(f"Context Score: {result.metadata.get('context_score', 1.0):.2f}x")
                print(f"Method: {result.method}")
                
                # Quick check
                sql = result.enhanced_sql.lower()
                if 'group by' in sql and 'profile_id' in sql:
                    print("✓ Correct: Individual profile analysis")
                elif 'group by' in sql and 'latitude' in sql:
                    print("✗ Wrong: Geographic analysis") 
                print("-" * 30)
        
        elif choice == '3':
            print("\nTesting Temperature Average Queries")
            print("-" * 40)
            queries = [
                "What is the average temperature across all profiles?",
                "average temperature",
                "temperature statistics"
            ]
            for q in queries:
                rag_system.test_and_execute(q, show_results=2)
                print()
        
        elif choice == '4':
            print("\nTesting Temperature Depth Distribution")
            print("-" * 40)
            queries = [
                "Show me temperature distribution at different depths",
                "temperature by depth zones", 
                "thermal stratification"
            ]
            for q in queries:
                rag_system.test_and_execute(q, show_results=3)
                print()
        
        elif choice == '5':
            print("\nTesting All Temperature Queries")
            print("-" * 40)
            all_queries = [
                "What is the average temperature across all profiles?",
                "Show me temperature distribution at different depths",
                "temperature by depth zones",
                "thermal stratification analysis", 
                "ocean temperature statistics"
            ]
            for q in all_queries:
                rag_system.test_and_execute(q, show_results=2)
                print()
        
        elif choice == '6':
            query = input("Enter query for context-aware analysis: ").strip()
            if query:
                print(f"\nContext-Aware Analysis for: '{query}'")
                print("-" * 50)
                result = rag_system.process_query(query)
                intent_info = result.metadata.get('query_intent', {})
                
                print("Intent Analysis:")
                print(f"  Intent: {intent_info.get('intent', 'unknown')}")
                print(f"  Grouping Level: {intent_info.get('grouping_level', 'unknown')}")
                print(f"  Parameters: {intent_info.get('parameters', [])}")
                print(f"  Operations: {intent_info.get('operations', [])}")
                print(f"  Confidence: {intent_info.get('confidence', 0.0):.3f}")
                
                print("\nSimilarity Analysis:")
                print(f"  Base Similarity: {result.metadata.get('base_similarity', 0):.4f}")
                print(f"  Context Score: {result.metadata.get('context_score', 1.0):.2f}x")
                print(f"  Context Similarity: {result.similarity:.4f}")
                print(f"  Method: {result.method}")
                
                print(f"\nGenerated SQL Preview:")
                sql_preview = result.enhanced_sql[:100] + "..." if len(result.enhanced_sql) > 100 else result.enhanced_sql
                print(f"  {sql_preview}")
        
        elif choice == '7':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    main()