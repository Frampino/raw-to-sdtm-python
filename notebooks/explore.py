#import di pandas
import pandas as pd

#lettura dataframe con pandas
raw = pd.read_csv("data/raw/dm_raw.csv", dtype=str)
ref = pd.read_csv("data/reference/dm.csv", dtype=str)

#comandi print per visualizzare file input
print (raw.shape, ref.shape)
print (list(raw.columns))
print (list(ref.columns))
print (raw["PATNUM"].nunique(), ref["USUBJID"].nunique())

#
for p in ["701-1015", "701-1023", "718-1427"]:
    print("=" * 60, p)
    print(raw[raw["PATNUM"] == p].T)
    print(ref[ref["SUBJID"] == p.split("-")[1]].T)

m = raw.merge(ref, left_on="PATNUM", right_on=ref["USUBJID"].str[3:])
col = pd.to_datetime(m["COL_DT"], format=("%m/%d/%Y"))
calc = [(c - pd.DateOffset(years=int(a))).strftime("%Y-%m-%d") for c, a in zip(col, m["IT.AGE"])]
print(len(m), (pd.Series(calc) == m["BRTHDTC"]).mean())

#lezione 2
# %% Indagine RFENDTC
ds = pd.read_csv("data/raw/ds_raw.csv", dtype=str)
ref = pd.read_csv("data/reference/dm.csv", dtype=str)
print(ds[ds["PATNUM"] == "701-1023"][["INSTANCE", "IT.DSDECOD", "OTHERSP", "IT.DSSTDAT"]])
print(ref[ref["SUBJID"] == "1023"][["RFSTDTC", "RFENDTC", "RFXENDTC"]])



# %% AE: prima occhiata
ae_raw = pd.read_csv("data/raw/ae_raw.csv", dtype=str)
ae = pd.read_csv("data/reference/ae.csv", dtype=str)
print(ae_raw.shape, ae.shape)
print(list(ae_raw.columns))
print(list(ae.columns))
print(ae_raw["PATNUM"].value_counts().head())
# %%
