import pandas as pd


# ============================================================
# PHASE 10 - MULTI-STEP FUTURE TARGET GENERATION
# ============================================================

INPUT_FILE = "data/phase8_sequential_network_data.csv"
OUTPUT_FILE = "data/phase10_multistep_targets.csv"


# ------------------------------------------------------------
# 1. Load sequential network dataset
# ------------------------------------------------------------

df = pd.read_csv(INPUT_FILE)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])


# ------------------------------------------------------------
# 2. Create future targets
# ------------------------------------------------------------
# shift(-1) = next observation
# shift(-2) = two observations ahead
# shift(-3) = three observations ahead
# shift(-4) = four observations ahead
#
# These represent approximately:
# +1 -> ~15-16 seconds
# +2 -> ~30-32 seconds
# +3 -> ~45-48 seconds
# +4 -> ~60-64 seconds
#
# Actual intervals vary, so these are step-based horizons.

for horizon in range(1, 5):

    df[f"future_latency_{horizon}"] = (
        df["avg_latency_ms"].shift(-horizon)
    )

    df[f"future_jitter_{horizon}"] = (
        df["jitter_ms"].shift(-horizon)
    )

    df[f"future_packet_loss_{horizon}"] = (
        df["packet_loss_percent"].shift(-horizon)
    )


# ------------------------------------------------------------
# 3. Remove rows without complete future targets
# ------------------------------------------------------------

target_columns = []

for horizon in range(1, 5):

    target_columns.extend([
        f"future_latency_{horizon}",
        f"future_jitter_{horizon}",
        f"future_packet_loss_{horizon}"
    ])


df_clean = df.dropna(
    subset=target_columns
).copy()


# ------------------------------------------------------------
# 4. Save dataset
# ------------------------------------------------------------

df_clean.to_csv(
    OUTPUT_FILE,
    index=False
)


# ------------------------------------------------------------
# 5. Display information
# ------------------------------------------------------------

print("=" * 65)
print("PHASE 10 - MULTI-STEP FUTURE TARGET GENERATION")
print("=" * 65)

print("Input dataset:", INPUT_FILE)
print("Original rows:", len(df))
print("Final rows:", len(df_clean))
print("Removed rows:", len(df) - len(df_clean))

print("\nFuture horizons created:")

for horizon in range(1, 5):

    print(
        f"+{horizon}: "
        f"future_latency_{horizon}, "
        f"future_jitter_{horizon}, "
        f"future_packet_loss_{horizon}"
    )


print("\nFinal columns:")
print(df_clean.columns.tolist())


print("\nFirst 3 rows:")
print(
    df_clean.head(3).to_string(
        index=False
    )
)


print("\nDataset saved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 65)
print("PHASE 10 TARGET GENERATION COMPLETE")
print("=" * 65)
