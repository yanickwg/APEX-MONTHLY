import yfinance as yf
import pandas as pd
import requests
import os

# --- CONFIGURATION APEX 4+ ---
DCA_MENSUEL = 1000

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
    
    # Calcul de la dérive (SMA 100)
    sma100 = float(close.rolling(100).mean().iloc[-1])
    derive = ((price - sma100) / sma100) * 100
    return price, derive

def check_monthly():
    if not WEBHOOK_URL:
        print("Erreur: Secret DISCORD_WEBHOOK manquant.")
        return

    msg = "🏛️ **STRATÉGIE APEX 4+ : ORDRE MENSUEL**\n"
    msg += f"💰 **Budget DCA : {DCA_MENSUEL} €**\n"
    msg += "------------------------------------------\n\n"
    
    data = []
    for name, ticker in ASSETS.items():
        try:
            df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, progress=False)
            price, derive = get_monthly_metrics(df)
            data.append({"name": name, "price": price, "derive": derive})
        except Exception as e:
            print(f"Erreur sur {name}: {e}")
            continue

    # Tri par dérive la plus faible (priorité d'achat)
    data.sort(key=lambda x: x['derive'])

    msg += "📊 **ANALYSE DES ALLOCATIONS :**\n"
    for d in data:
        msg += f"• {d['name']} : {d['derive']:+.1f}%\n"

    msg += "\n------------------------------------------\n"
    msg += "🎯 **ORDRE D'ACHAT DU MOIS :**\n"
    msg += f"Investir les **{DCA_MENSUEL} €** sur :\n"
    msg += f"👉 **{data[0]['name']}**\n\n"
    msg += "💡 *Note :* On renforce l'actif le plus en retard pour forcer le rééquilibrage."

    requests.post(WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    check_monthly()
