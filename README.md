# Singapore HDB Resale Price Dashboard & Data Pipeline

- An automated, cloud-native data pipeline and interactive web dashboard built to track and analyze the latest public housing resale transactions in Singapore. 

- This project completely automates the extraction of fresh monthly transaction data directly from the official government portal (`data.gov.sg`), packages it into a 
highly compressed, high-performance **Parquet** data format, 
and updates a live web dashboard without any manual intervention.

---

## 🚀 The Automation Architecture

To keep the application fast and cost-effective, the pipeline splits data retrieval from data visualization:

```text
 [Data.gov.sg Portal] ➔ (Every Friday 9:00 AM) ➔ [GitHub Actions Cloud Machine]
                                                        │
                                             Runs 'get_hdb_data.py'
                                                        │
 [Live Streamlit App] 🔀 (Auto-Reloads) 🔀 [data/latest_hdb_resale_prices.parquet]

```

- **Every Friday at 9:00 AM (SGT):** A GitHub Actions workflow wakes up automatically in the cloud.

- **Data Extraction:** The workflow installs Python, executes get_hdb_data.py, completes a two-step handshake with the Data.gov.sg V2 API, identifies the newest monthly data slice, and downloads it.

- **Storage Optimization:** The raw data is saved into the data/ folder as a compressed Parquet file (shrinking the file footprint from over 21MB down to under 5MB).

- **Automated Commit:** The GitHub Bot automatically commits and pushes the updated data back into this repository.

-**Instant Frontend Update:** Streamlit Cloud detects the data modification on GitHub, clears its internal memory cache, and serves the latest property figures to users instantly.

## 📂 Repository Structure

**Plaintext**
```text
📂 Streamlit_HDB/               # Main repository root folder
┃  ┣ 📂 .github/workflows/
┃  ┃  ┗ 📜 hdb_updater.yml       # The automated clock timer (Runs every Friday 9AM)
┃  ┣ 📂 data/
┃  ┃  ┗ 📜 latest_hdb_resale_prices.parquet  # The active, compressed data file (<5MB)
┃  ┣ 📜 .gitignore               # Privacy guard file (Prevents local junk files from uploading)
┃  ┣ 📜 app.py                     # The main Streamlit visualization dashboard script
┃  ┣ 📜 get_hdb_data.py            # The standalone REST API data downloader script
┃  ┗ 📜 requirements.txt           # The shopping list of tools required by the cloud servers
```

## 🛠️ Technology Stack & Dependencies 

The project relies on a clean, modern data engineering stack specified in requirements.txt:

- requests: Handles communication and security handshakes with government REST APIs.

- pandas: Serves as our virtual data engine for structured tables and cleaning.

- pyarrow: The structural backbone required to compress and read Parquet files efficiently.

- streamlit: Turns our backend data framework into an interactive web interface.

## ⏱️ The Automation Clock (CRON Syntax Explained)

The automated workflow inside .github/workflows/hdb_updater.yml is governed by a standard cloud timer expression:
cron: '0 1 * * 5'

``` 0: Exact Minute (00) ```

``` 1: Exact Hour (1:00 AM UTC, which maps perfectly to 9:00 AM Singapore Time because Singapore is 8 hours ahead of universal time). ```

``` * *: Runs every day of the month, every month of the year. ```

``` 5: Runs specifically on day 5 of the week (Friday). ```

