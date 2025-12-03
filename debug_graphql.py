import requests
import json

URL = "https://dgidb.org/api/graphql"

def run_query(query):
    print(f"\nQuery:\n{query}")
    try:
        response = requests.post(URL, json={'query': query}, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

# Attempt 1: Relay Style (nodes)
query_1 = """
{
  genes(names: ["TP53"]) {
    nodes {
      symbol
      name
      interactions {
        drug {
          name
        }
      }
    }
  }
}
"""

# Attempt 2: Relay Style (edges)
query_2 = """
{
  genes(names: ["TP53"]) {
    edges {
      node {
        symbol
        name
      }
    }
  }
}
"""

# Attempt 3: Drug Query (Corrected)
query_3 = """
{
  drugs(names: ["NEBIVOLOL"]) {
    nodes {
      name
      interactions {
        gene {
          name
        }
      }
    }
  }
}
"""

if __name__ == "__main__":
    print("--- Testing GraphQL Queries ---")
    run_query(query_1)
    run_query(query_3)
