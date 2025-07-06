# Firework
APR aggregator project for Ethereum Global Cannes




# 🛠️ Installation Guide

Follow these steps to set up and run the APR Data Logger project on your local machine.

---

## Step 1: Clone or Download the Project


```bash
git clone https://github.com/0xemkey/firework.git
cd apr-aggregator
```

## Step 2: Create a Virtual Environment
We strongly recommend using a virtual environment for dependency isolation:

``` bash

python -m venv apr_env
```

## Step 3: Activate the Virtual Environment
### On Windows:
```bash
apr_env\Scripts\activate
```
### On Mac/Linux:
```bash
source apr_env/bin/activate
```

## Step 4: Install Required Dependencies
Install Python libraries:
```bash
pip install pandas openpyxl playwright nest_asyncio uagents
Install Playwright browser binaries:
```
```bash
playwright install
```
Or alternatively, use the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

## Step 5: Run the Scripts
Run the script to fetch APR values:

### Monthly Payment 
```bash
python monthlypayment.py
```

### Scrape APR values for $WETH and $USDC from Euler and Katana on Ethereum Mainnet.
```bash
python turtleAprScraper.py
python eulerAprScraper.py
```
### Run the Agent
```bash
python agent.py
```
