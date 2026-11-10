
"Si parte da due tabelle. Il foglio grezzo che arriva dall’EDC (dm_raw),"
" e un foglio nuovo e vuoto che devo riempire con le regole SDTM (dm)."
" Ogni riga del codice riempie una colonna del foglio nuovo."

import pandas as pd

# funzione per convertire le date in formato ISO 8601
def a_iso(colonna, formato):
    """Converte una colonna di date grezze nel formato ISO 8601 (aaaa-mm-gg)."""
    return pd.to_datetime(colonna, format=formato).dt.strftime("%Y-%m-%d")

# funzione per derivare il dataset DM a partire dai dati grezzi e dai dataset DS ed EC
def derive_dm(dm_raw, ds_raw, ec_raw):
    dm = pd.DataFrame()

    # Identificativi
    dm["STUDYID"] = dm_raw["STUDY"]
    dm["DOMAIN"] = "DM"
    dm["USUBJID"] = "01-" + dm_raw["PATNUM"]
    dm["SUBJID"] = dm_raw["PATNUM"].str.split("-").str[1]
    dm["SITEID"] = dm_raw["PATNUM"].str.split("-").str[0]

    # Copia colonna it.age in colonna age
    dm["AGE"] = dm_raw["IT.AGE"]
    # crea una colonna uguale con le stesse informazioni ma con l'unità di misura "YEARS"
    dm["AGEU"] = "YEARS"
    # mappa i valori della colonna it.sex in una nuova colonna con i valori "F" e "M"
    dm["SEX"] = dm_raw["IT.SEX"].map({"Female": "F", "Male": "M"})
    # mappa i valori della colonna it.race in una nuova colonna con i valori in maiuscolo
    dm["RACE"] = dm_raw["IT.RACE"].str.upper()
    # mappa i valori della colonna it.ethnic in una nuova colonna con i valori in maiuscolo
    dm["ETHNIC"] = dm_raw["IT.ETHNIC"].str.upper()
    # crea una colonna uguale con le stesse informazioni
    dm["COUNTRY"] = dm_raw["COUNTRY"]
    # crea una colonna uguale con le stesse informazioni
    dm["ARMCD"] = dm_raw["PLANNED_ARMCD"]

    # mappa i valori della colonna planned_arm in una nuova colonna con i valori in maiuscolo
    bracci = {"Xan High": "Xanomeline High Dose", "Xan Low": "Xanomeline Low Dose"}
    dm["ARM"] = dm_raw["PLANNED_ARM"].replace(bracci)

    # copia colonna actual_armcd in colonna actarmcd
    dm["ACTARMCD"] = dm_raw["ACTUAL_ARMCD"]

    # mappa i valori della colonna actual_arm in una nuova colonna con i valori in maiuscolo
    dm["ACTARM"] = dm_raw["ACTUAL_ARM"].replace(bracci)

    # mappa i valori della colonna it.arm in una nuova colonna con i valori in maiuscolo
    dm["ARMNRS"] = dm_raw["PLANNED_ARMCD"].map({"Scrnfail": "SCREEN FAILURE"})

    # è sempre vuota
    dm["ACTARMUD"] = None
    
    
    # calcolo della data di raccolta dei dati demografici a partire dalla colonna COL_DT del file dm_raw
    dm["DMDTC"] = a_iso(dm_raw["COL_DT"], "%m/%d/%Y")

    # calcolo della data di screening a partire dalla colonna IC_DT del file dm_raw
    dm["RFICDTC"] = a_iso(dm_raw["IC_DT"], "%m/%d/%Y")

    # calcolo della data di nascita a partire dalla data di screening e dall'età
    col = pd.to_datetime(dm_raw["COL_DT"], format="%m/%d/%Y")
    dm["BRTHDTC"] = [(c - pd.DateOffset(years=int(a))).strftime("%Y-%m-%d")
        for c, a in zip(col, dm_raw["IT.AGE"])]


    # prima/ultima dose: min/max delle date EC per soggetto (convertite in data prima del min/max)
    
    # creazione della colonna RFXSTDTC a partire dalla colonna IT.ECSTDAT del file ec_raw
    inizio = pd.to_datetime(ec_raw["IT.ECSTDAT"], format="%d-%b-%Y")
    prima_dose = inizio.groupby(ec_raw["PATNUM"]).min()
    dm["RFXSTDTC"] = dm_raw["PATNUM"].map(prima_dose).dt.strftime("%Y-%m-%d")

    # creazione della colonna RFXENDTC a partire dalla colonna IT.ECENDAT del file ec_raw
    fine = pd.to_datetime(ec_raw["IT.ECENDAT"], format="%d-%b-%Y")
    ultima_dose = fine.groupby(ec_raw["PATNUM"]).max()
    dm["RFXENDTC"] = dm_raw["PATNUM"].map(ultima_dose).dt.strftime("%Y-%m-%d")

    # copia RFSTDTC perchè in questo studio coincide con RFXSTDTC
    dm["RFSTDTC"] = dm["RFXSTDTC"]

    # DEATHDT è ripetuta uguale su tutte le righe di chi è morto ed è vuota per gli altri
        # tiene solo la prima data di morte per soggetto, se esiste, e la converte in formato ISO 8601
    morte = ds_raw["DEATHDT"].groupby(ds_raw["PATNUM"]).first()
    dm["DTHDTC"] = a_iso(dm_raw["PATNUM"].map(morte), "%m/%d/%Y")
    
    # DTHFL = Y se c'è una data di morte
    dm["DTHFL"] = dm["DTHDTC"].notna().map({True: "Y", False: None})

    # RFPENDTC: data+ora più recente in DS per soggetto (fillna evita che l'ora mancante svuoti la data)
    
    iso = a_iso(ds_raw["DSDTCOL"], "%m-%d-%Y") + ("T" + ds_raw["DSTMCOL"]).fillna("")
    fine = iso.groupby(ds_raw["PATNUM"]).max()
    dm["RFPENDTC"] = dm_raw["PATNUM"].map(fine)

    # giorno di studio da RFSTDTC (prima dose): niente giorno 0, quindi +1 se >= 0
    # calcolo della differenza in giorni tra DMDTC e RFSTDTC
    dm["DMDY"] = (pd.to_datetime(dm["DMDTC"]) - pd.to_datetime(dm["RFSTDTC"])).dt.days
    dm["DMDY"] = dm["DMDY"].where(dm["DMDY"] < 0, dm["DMDY"] + 1).astype("Int64")
    # se DMDTC o RFSTDTC sono vuoti, DMDY è vuoto. dm["DMDY"] = giorni.where(CONDIZIONE, ALTRIMENTI).astype("Int64")

    # RFENDTC: data della riga DS di fine trattamento (DSDECOD non vuoto e diverso da Randomized); vuota per gli screen failure
    disp = ds_raw[ds_raw["IT.DSDECOD"].notna() & (ds_raw["IT.DSDECOD"] != "Randomized")]
    
    fine = disp["IT.DSSTDAT"].groupby(disp["PATNUM"]).first()
    
    dm["RFENDTC"] = a_iso(dm_raw["PATNUM"].map(fine), "%m-%d-%Y")
    
    dm["RFENDTC"] = dm["RFENDTC"].where(dm["RFSTDTC"].notna())
    


    return dm
