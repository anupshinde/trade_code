# Gold-Silver Ratio Classic Threshold Strategy Backtest

import pandas as pd
import matplotlib.pyplot as plt

# === Load Data ===
gold_file = "../../data/GC_full_1day_continuous_UNadjusted.csv"
silver_file = "../../data/SI_full_1day_continuous_UNadjusted.csv"

col_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest']
gold_df = pd.read_csv(gold_file, header=None, names=col_names)
silver_df = pd.read_csv(silver_file, header=None, names=col_names)

# Convert date and keep only necessary columns
gold_df['Date'] = pd.to_datetime(gold_df['Date'])
silver_df['Date'] = pd.to_datetime(silver_df['Date'])

gold_df = gold_df[['Date', 'Close']].rename(columns={'Close': 'Gold_Close'})
silver_df = silver_df[['Date', 'Close']].rename(columns={'Close': 'Silver_Close'})

# Merge and calculate GSR
merged_df = pd.merge(gold_df, silver_df, on='Date').sort_values('Date')
merged_df['GSR'] = merged_df['Gold_Close'] / merged_df['Silver_Close']

# === Strategy Parameters ===
ENTRY_THRESHOLD = 90
EXIT_THRESHOLD = 75
GOLD_CONTRACT_SIZE = 100      # 1 GC = 100 oz
SILVER_CONTRACT_SIZE = 50000  # 10 SI = 50,000 oz

# === Backtest Logic ===
entries = []
exits = []
in_position = False

for i in range(len(merged_df)):
    row = merged_df.iloc[i]
    date, gsr = row['Date'], row['GSR']
    gold_price, silver_price = row['Gold_Close'], row['Silver_Close']

    if not in_position and gsr >= ENTRY_THRESHOLD:
        entries.append({
            'Entry Date': date,
            'Entry GSR': gsr,
            'Gold Entry': gold_price,
            'Silver Entry': silver_price
        })
        in_position = True

    elif in_position and gsr < EXIT_THRESHOLD:
        exits.append({
            'Exit Date': date,
            'Exit GSR': gsr,
            'Gold Exit': gold_price,
            'Silver Exit': silver_price
        })
        in_position = False

# === Match Entries and Exits ===
results = []
for entry, exit_ in zip(entries, exits):
    pnl_gold = (entry['Gold Entry'] - exit_['Gold Exit']) * GOLD_CONTRACT_SIZE
    pnl_silver = (exit_['Silver Exit'] - entry['Silver Entry']) * SILVER_CONTRACT_SIZE
    total_pnl = pnl_gold + pnl_silver

    results.append({
        'Entry Date': entry['Entry Date'],
        'Exit Date': exit_['Exit Date'],
        'Entry GSR': entry['Entry GSR'],
        'Exit GSR': exit_['Exit GSR'],
        'Gold Entry': entry['Gold Entry'],
        'Gold Exit': exit_['Gold Exit'],
        'Silver Entry': entry['Silver Entry'],
        'Silver Exit': exit_['Silver Exit'],
        'Gold PnL ($)': pnl_gold,
        'Silver PnL ($)': pnl_silver,
        'Total PnL ($)': total_pnl
    })

# === Convert to DataFrame ===
backtest_df = pd.DataFrame(results)
backtest_df['Cumulative PnL'] = backtest_df['Total PnL ($)'].cumsum()

# === Plot Cumulative PnL ===
plt.figure(figsize=(12, 6))
plt.plot(backtest_df['Exit Date'], backtest_df['Cumulative PnL'], marker='o', linestyle='-')
plt.title('Cumulative PnL: GSR ≥ 90 Entry, GSR < 75 Exit')
plt.xlabel('Exit Date')
plt.ylabel('Cumulative PnL ($)')
plt.grid(True)
plt.tight_layout()
plt.show()

# === Show Summary ===
print("\nBacktest Summary:")
print(backtest_df)
