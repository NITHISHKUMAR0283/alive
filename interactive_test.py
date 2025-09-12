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
    rag_system.setup_system()
    
    print("\n" + "="*60)
    print("INTERACTIVE RAG TESTING")
    print("="*60)
    print("Enhanced with your dynamic temperature queries!")
    print("Total queries in ChromaDB: 386")
    
    while True:
        print("\nOptions:")
        print("1. Test a custom query")
        print("2. Test temperature average query")
        print("3. Test temperature depth distribution")
        print("4. Test all temperature queries")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            query = input("Enter your query: ").strip()
            if query:
                print(f"\nTesting: {query}")
                print("-" * 40)
                rag_system.test_and_execute(query, show_results=3)
        
        elif choice == '2':
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
        
        elif choice == '3':
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
        
        elif choice == '4':
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
        
        elif choice == '5':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()