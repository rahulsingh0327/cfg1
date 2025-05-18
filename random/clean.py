import pandas as pd
import datetime
from sklearn.preprocessing import StandardScaler

# === CONFIGURATION ===
INPUT_FILE = "multithreaded_memory_log_BT7274_BT7274.csv"  # Change if needed
OUTPUT_FILE = "cleaned_memory_dataset.csv"
PAGE_FAULT_CAP = 1_000_000
ROLLING_WINDOW = 3  # For smoothing
SWAP_THRESHOLD_MB = 1000  # Swap > 1GB → swap pressure
RAM_THRESHOLD_MB = 15000  # RAM > 15GB → memory pressure
FAULT_THRESHOLD = 300     # Page faults/sec > 300 → swap pressure

# === LOAD DATA ===
df = pd.read_csv(INPUT_FILE)

# === 1. Convert Timestamp → Readable Format ===
df["Readable_Time"] = df["Timestamp"].apply(
    lambda ts: datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
)

# === 2. Clip huge spikes in Page Faults ===
df["Page_Faults_Delta"] = df["Page_Faults_Delta"].clip(upper=PAGE_FAULT_CAP)

# === 3. Rolling Average (Optional Smoothing) ===
df["Page_Faults_Smoothed"] = df["Page_Faults_Delta"].rolling(
    window=ROLLING_WINDOW, min_periods=1
).mean()

# === 4. Create Swap_Label (1 = memory pressure, 0 = normal) ===
df["Swap_Label"] = (
    (df["Page_Faults_Delta"] > FAULT_THRESHOLD) |
    (df["RAM_Usage_MB"] > RAM_THRESHOLD_MB) |
    (df["Swap_Usage_MB"] > SWAP_THRESHOLD_MB)
).astype(int)

# === 5. Normalize Page Faults for ML (Optional) ===
scaler = StandardScaler()
df["Page_Faults_Delta_Scaled"] = scaler.fit_transform(df[["Page_Faults_Delta"]])

# === 6. Save cleaned dataset ===
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Cleaned & labeled dataset saved as: {OUTPUT_FILE}")