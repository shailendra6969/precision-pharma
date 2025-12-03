import logging
from src.pipeline.external_apis import OpenFDAClient, PubChemClient, DGIdbClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_search(query):
    print(f"--- Debugging Search for: '{query}' ---")
    
    # 1. OpenFDA Search
    print("\n1. OpenFDA Search:")
    fda = OpenFDAClient()
    results = fda.search_drugs(query)
    print(f"Results: {results}")
    
    if results:
        drug_name = results[0]
        print(f"Top Result: {drug_name}")
        
        # 2. OpenFDA Label (Generic Name)
        print("\n2. OpenFDA Label (Generic Name):")
        label = fda.get_drug_label(drug_name)
        if label and 'openfda' in label:
            generic = label['openfda'].get('generic_name')
            print(f"Generic Name: {generic}")
        else:
            print("No generic name found in label.")
            
        # 3. PubChem
        print("\n3. PubChem Data:")
        pubchem = PubChemClient()
        data = pubchem.get_compound_data(drug_name)
        if data:
            print("PubChem Data Found")
        else:
            print("PubChem Data NOT Found")
            
        # 4. DGIdb
        print("\n4. DGIdb Interactions:")
        dgidb = DGIdbClient()
        interactions = dgidb.get_genes_for_drug(drug_name)
        print(f"Interactions (Brand): {len(interactions)}")
        
        if label and 'openfda' in label:
             generic_names = label['openfda'].get('generic_name', [])
             if generic_names:
                 generic = generic_names[0]
                 interactions_generic = dgidb.get_genes_for_drug(generic)
                 print(f"Interactions (Generic '{generic}'): {len(interactions_generic)}")

if __name__ == "__main__":
    debug_search("nebivolol")
