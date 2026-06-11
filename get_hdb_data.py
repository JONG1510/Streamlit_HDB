import requests
import pandas as pd
from datetime import datetime
from pprint import pprint

def get_latest_hdb_data():
    print("Connecting to Data.gov.sg V2 Collection API...")
    collection_id = 189        # 189 is the unique identifier for the HDB Resale Prices collection on data.gov.sg; others are 1569, 578 etc   
    collection_url = f"https://api-production.data.gov.sg/v2/public/api/collections/{collection_id}/metadata?withDatasetMetadata=true"
        
    response = requests.get(collection_url)
    meta_res = response.json()
    
    # Extract the dataset catalog list
    dataset_list = meta_res['data']['datasetMetadata']

    print("\n--- Scanning and Parsing Timeframes ---")
    latest_date = None
    latest_dataset = None

    for ds in dataset_list:
        # Strip timezone offset (+08:00) to safely parse string
        clean_date_str = ds['coverageEnd'].split("+")[0]
        parsed_date = datetime.strptime(clean_date_str, "%Y-%m-%dT%H:%M:%S")

        print(f"📦 ID: {ds['datasetId']} ➔ Coverage Ends: {parsed_date.strftime('%B %d, %Y')}")

        if latest_date is None or parsed_date > latest_date:
            latest_date = parsed_date
            latest_dataset = ds
        
    latest_id = latest_dataset["datasetId"]
    print("=" * 60)
    print(f"🎯 Target Dataset Name: {latest_dataset['name']}")
    print(f"   Dataset ID:          {latest_id}")
    print(f"   Coverage End Date:   {latest_date.strftime('%Y-%m-%d')}")
    print("=" * 60)   

    # Execute official Download Handshake (Initiate & Poll)
    print(f"\nInitiating download session for segment...")
    initiate_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{latest_id}/initiate-download"
    init_res = requests.get(initiate_url).json()
    
    poll_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{latest_id}/poll-download"
    poll_res = requests.get(poll_url).json()
    
    final_download_url = poll_res["data"]["url"]
    print(f"✅ Secure URL Generated: {final_download_url}")

    # Read data directly into memory
    print("Streaming transactions into memory...")
    df = pd.read_csv(final_download_url)
    
    return df

# Execute standalone test and cloud automation
if __name__ == "__main__":
    # 1. Run the extraction function to pull data from data.gov.sg
    hdb_df = get_latest_hdb_data()
    print(f"\n🚀 Success! Loaded {len(hdb_df):,} active rows.")
    
    # 2. Define the relative path to save inside your 'data' folder as a parquet file
    # Note: We use a forward slash '/' which both Windows and GitHub (Linux) understand perfectly
    target_parquet_path = "data/latest_hdb_resale_prices.parquet"
    
    # 3. Save directly as a compressed parquet file
    print(f"💾 Saving data to {target_parquet_path}...")
    hdb_df.to_parquet(target_parquet_path, index=False)
    
    print("🎯 Local test process complete!")