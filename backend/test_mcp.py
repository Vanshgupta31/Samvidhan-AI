import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import query_legal_assistant

def test_query():
    print("Testing query_legal_assistant...")
    try:
        response = query_legal_assistant("What is the punishment for murder in India?")
        print("\n--- Response ---\n")
        print(response)
        print("\n--- End Response ---\n")
        
        if "Murder" in response or "IPC" in response or "BNS" in response:
            print("Test Passed: Response contains expected keywords.")
        else:
            print("Test Warning: Response might not be accurate.")
            
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_query()
