import pandas as pd

# funzione per convertire le date in formato ISO 8601
def a_iso(colonna, formato):
    """Converte una colonna di date grezze nel formato ISO 8601 (aaaa-mm-gg)."""
    return pd.to_datetime(colonna, format=formato).dt.strftime("%Y-%m-%d")

#funzione per derivare il dataset AE a partire dai dati grezzi e dal dataset DM
def derive_ae(ae_raw, dm):
    ae = pd.DataFrame()

    # Identificativi (fatti come esempio)
    ae["STUDYID"] = ae_raw["STUDY"]
    ae["DOMAIN"] = "AE"
    ae["USUBJID"] = "01-" + ae_raw["PATNUM"]

    # Passo 1 - TODO: AETERM e la codifica MedDRA
    ae["AETERM"] = ae_raw["IT.AETERM"].str.upper()

    #   AELLT, AEDECOD, AEHLT, AEHLGT, AEBODSYS, AESOC
    for c in ["AELLT", "AEDECOD", "AEHLT", "AEHLGT", "AEBODSYS", "AESOC"]:
        ae[c] = ae_raw[c]
    
    #   AELLTCD, AEPTCD, AEHLTCD, AEHLGTCD, AEBDSYCD, AESOCCD
    for c in ["AELLTCD", "AEPTCD", "AEHLTCD", "AEHLGTCD", "AEBDSYCD", "AESOCCD"]:
            ae[c] = ae_raw[c]

    # Passo 2 - TODO: gravità, serietà, azione, relazione, esito, e le variabili di sicurezza
    #   AESEV, AESER, AEACN, AEREL, AEOUT
    #   AESCAN, AESCONG, AESDISAB, AESDTH, AESHOSP, AESLIFE, AESOD
    ae["AESEV"] = ae_raw["IT.AESEV"].map({"Mild Adverse Event": "MILD", "Moderate Adverse Event": "MODERATE", "Severe Adverse Event": "SEVERE"})
    ae["AESER"] = ae_raw["IT.AESER"].map({"Yes": "Y", "No": "N"})
    ae["AEACN"] = ae_raw["IT.AEACN"]
    ae["AEREL"] = ae_raw["IT.AEREL"].map({"Not Related": "NONE", "Possibly Related": "POSSIBLE", "Probably Related": "PROBABLE", "Remote": "REMOTE"})
    ae["AEOUT"] = ae_raw["AEOUTCOME"].str.upper()
    ae["AESCAN"] = ae_raw["AESCAN"].map({"Yes": "Y", "No": "N"})
    ae["AESCONG"] = ae_raw["AESCNO"].map({"Yes": "Y", "No": "N"})
    ae["AESDISAB"] = ae_raw["AEDIS"].map({"Yes": "Y", "No": "N"})
    ae["AESOD"] = ae_raw["AESOD"].map({"Yes": "Y", "No": "N"})
    ae["AESDTH"] = ae_raw["IT.AESDTH"].map({"Yes": "Y", "No": "N"})
    ae["AESHOSP"] = ae_raw["IT.AESHOSP"].map({"Yes": "Y", "No": "N"})
    ae["AESLIFE"] = ae_raw["IT.AESLIFE"].map({"Yes": "Y", "No": "N"})

    # Passo 3 - TODO: date di inizio e fine evento, con conversione in formato ISO 8601
    #   AEDTC, AESTDTC, AEENDTC
    ae["AEDTC"] = a_iso(ae_raw["AEDTCOL"], "%m/%d/%Y")
    #tiene le date complete e converte quelle; i buchi che restano (le date parziali) le riempie con il valore grezzo”.
    completa = ae_raw["IT.AESTDAT"].str.len() == 10
    ae["AESTDTC"] = a_iso(ae_raw["IT.AESTDAT"].where(completa), "%m/%d/%Y").fillna(ae_raw["IT.AESTDAT"])
    # controlla se la lunghezza della stringa è 10 (formato completo) e converte solo quelle, lasciando le altre come sono.
    completa = ae_raw["IT.AEENDAT"].str.len() == 10
    ae["AEENDTC"] = a_iso(ae_raw["IT.AEENDAT"].where(completa), "%m/%d/%Y").fillna(ae_raw["IT.AEENDAT"])

    # Passo 4 - TODO: giorni di studio, con RFSTDTC preso da dm
    #   AESTDY, AEENDY 
    def giorno_studio(DMDTC, RFSTDTC):
        """Calcola il giorno di studio a partire da una data e dalla data di screening."""
        giorni = (pd.to_datetime(DMDTC, format="%Y-%m-%d", errors="coerce") - pd.to_datetime(RFSTDTC, format="%Y-%m-%d", errors="coerce")).dt.days
        return giorni.where(giorni < 0, giorni + 1).astype("Int64")

    #dm.set_index("USUBJID")["RFSTDTC"] trasforma DM in un dizionario “soggetto → prima dose”.
    # Poi .map() lo attacca a ogni evento del soggetto: se 701-1302 ha 23 eventi, la sua data arriva su tutte e 23 le righe.
    rif = ae["USUBJID"].map(dm.set_index("USUBJID")["RFSTDTC"]) #
    ae["AESTDY"] = giorno_studio(ae["AESTDTC"], rif)
    ae["AEENDY"] = giorno_studio(ae["AEENDTC"], rif)

    # Passo 5 - TODO: numero di sequenza
    #   AESEQ, AESPID
    #AESEQ è un numero d’ordine degli eventi dentro ogni soggetto: riparte da 1 per ogni USUBJID. Serve a identificare in modo unico ogni riga, insieme a USUBJID
    ae = ae.sort_values(["USUBJID", "AESTDTC", "AETERM"], kind="stable")   # 1. ordina
    ae["AESEQ"] = ae.groupby("USUBJID").cumcount() + 1                     # 2. numera
    ae = ae.sort_index()                                                    # 3. rimetti l'ordine originale
    return ae

    ae["AESPID"] = None  # AESPID non è richiesto in questo studio, quindi rimane vuoto