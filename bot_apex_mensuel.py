import yfinance as yf
import pandas as pd
import requests
import os
from datetime import datetime

# --- CONFIGURATION APEX 4+ PRO ---
CAPITAL_INITIAL = 10000
DCA_MENSUEL = 1000
DATE_DEBUT = "2025-01-01" # Ajuste la date de ton premier investissement

ASSETS = {
    "NASDAQ x2 (Amundi)": "LQQ.PA",
    "NASDAQ x2 (Wisdom)": "NDL2.L",
    "GOLD Physique": "GOLD.PA",
    "GOLD x2 (4RT8)": "4RT8.L",
    "BITCOIN (Réel)": "BTC-USD"
}

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def get_monthly_metrics(df):
    if isinstance(df.columns, pd.MultiIndex): 
        df.columns = df.columns.droplevel(1)
    close = df['Close'].squeeze()
    price = float(close.iloc[-1])
    sma100 = float(close.rolling(100).mean().iloc[-1])
    derive = ((price - sma100) / sma100) * 100
    return price, derive

def check_monthly():
    if not WEBHOOK_URL: return

    # Calcul du capital théorique injecté
    date_depart = datetime.strptime(DATE_DEBUT, "%Y-%m-%d")
    mois_ecoules = (datetime.now().year - date_depart.year) * 12 + datetime.now().month - date_depart.month
    capital_total_injecte = CAPITAL_INITIAL + (mois_ecoules * DCA_MENSUEL)

    msg = "🏛️ **STRATÉGIE APEX 4+ : GESTION DE CAPITAL**\n"
    msg += f"💰 **Capital total injecté : {capital_total_injecte:,.0f} €**\n"
    msg += f"➕ **DCA ce mois : {DCA_MENSUEL} €**\n"
    msg += "------------------------------------------\n\n"
    
    data = []
    for name, ticker in ASSETS.items():
        try:
            df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
            price, derive = get_monthly_metrics(df)
            data.append({"name": name, "price": price, "derive": derive})
        except: continue

    data.sort(key=lambda x: x['derive'])

    msg += "📊 **ANALYSE DES ALLOCATIONS :**\n"
    for d in data:
        msg += f"• {d['name']} : {d['derive']:+.1f}%\n"

    msg += "\n------------------------------------------\n"
    msg += "🎯 **ORDRE D'ACHAT DU MOIS :**\n"
    msg += f"Investir les **{DCA_MENSUEL} €** sur :\n"
    msg += f"👉 **{data[0]['name']}**\n\n"
    msg += f"💡 **Objectif 20%** : Ta cible par ligne est de **{capital_total_injecte / 5:,.0f} €**."

    requests.post(WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    check_monthly()
