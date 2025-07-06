from uagents import Agent, Context
import pandas as pd
import requests
import json

# Together.ai API bilgileri
API_KEY = "tgp_v1_eiutSVU38Nhrry-hrcmEMR8hqyri_N21YBh9A-DWPV4"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

# Agent tanımı
agent = Agent(
    name="profiled_advisor",
    port=8015,
    seed="buyer vital insect curtain middle snap climb twenty inject anchor goose lawn",
    endpoint=["http://localhost:8015/submit"],
    mailbox=True
)

# Kullanıcıdan yatırım profili alınır
def get_user_profile():
    print("👤 Let's understand your investor profile:\n")
    risk = input("1. Risk level? (low / medium / high): ").strip().lower()
    preference = input("2. What matters more? (yield / stability): ").strip().lower()
    duration_raw = input("3. Investment duration? (< 3 months / > 3 months): ").strip()
    
    if "3" in duration_raw and "<" in duration_raw:
        horizon = "under 3 months"
    else:
        horizon = "over 3 months"

    return {"risk": risk, "preference": preference, "horizon": horizon}


# CSV farklarını hesaplar
def compare_dataframes(df1, df2):
    differences = {}
    for column in df1.columns:
        if column in df2.columns and not df1[column].equals(df2[column]):
            diff_rows = df1[column] != df2[column]
            differences[column] = {
                "Euler": df1.loc[diff_rows, column].to_dict(),
                "Katana": df2.loc[diff_rows, column].to_dict()
            }
    return differences

# Together.ai ile kişisel analiz yaptırır
def analyze_with_profile(profile, differences):
    prompt = f"""
You are a DeFi investment advisor.

Below is a user investment profile:
- Risk level: {profile['risk']}
- Preference: {profile['preference']}
- Time horizon: {profile['horizon']}

APR differences between two protocols (Euler and Katana):
{json.dumps(differences, indent=2)}

Based on this profile and APR data:
→ Which protocol suits this user best and why?
→ Be specific and make a clear recommendation.
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [
            {"role": "system", "content": "You are a DeFi financial advisor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ API error: {e}"

# Başlangıçta soruları sorar ve analiz yapar
@agent.on_event("startup")
async def startup(ctx: Context):
    try:
        profile = get_user_profile()
        df1 = pd.read_csv("euler_apr_log_succeed.csv")
        df2 = pd.read_csv("turtle_apr_log.csv")
        differences = compare_dataframes(df1, df2)
        result = analyze_with_profile(profile, differences)
        ctx.logger.info("\n📊 🤖 Personalized Recommendation:\n" + result)
    except Exception as e:
        ctx.logger.error(f"Startup error: {e}")

# Agent başlatılır
if __name__ == "__main__":
    agent.run()
