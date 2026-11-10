import pandas as pd

# funzione per convertire le date in formato ISO 8601
def a_iso(colonna, formato):
    """Converte una colonna di date grezze nel formato ISO 8601 (aaaa-mm-gg)."""
    return pd.to_datetime(colonna, format=formato).dt.strftime("%Y-%m-%d")

#funzione per derivare il dataset AE a partire dai dati grezzi e dal dataset DM
def derive_ae(ae_raw, dm):
    ae = pd.DataFrame()

    # Identificativi
    ae["STUDYID"] = ae_raw["STUDY"]
    ae["DOMAIN"] = "AE"
    ae["USUBJID"] = "01-" + ae_raw["PATNUM"]

    # Copia la colonna ae_raw["IT.AETERM"] in maiuscolo nella colonna ae["AETERM"]
    ae["AETERM"] = ae_raw["IT.AETERM"].str.upper()

    #   ciclo per copiare le colonne AELLT, AEDECOD, AEHLT, AEHLGT, AEBODSYS, AESOC
    for c in ["AELLT", "AEDECOD", "AEHLT", "AEHLGT", "AEBODSYS", "AESOC"]:
        ae[c] = ae_raw[c]
    
    #   ciclo per copiare le colonne AELLTCD, AEPTCD, AEHLTCD, AEHLGTCD, AEBDSYCD, AESOCCD
    for c in ["AELLTCD", "AEPTCD", "AEHLTCD", "AEHLGTCD", "AEBDSYCD", "AESOCCD"]:
            ae[c] = ae_raw[c]

    # mappa i valori della colonna it.aesev in una nuova colonna con i valori "MILD", "MODERATE", "SEVERE"
    ae["AESEV"] = ae_raw["IT.AESEV"].map({"Mild Adverse Event": "MILD", "Moderate Adverse Event": "MODERATE", "Severe Adverse Event": "SEVERE"})
    #mappa i valori della colonna it.aeser in una nuova colonna con i valori "Y" e "N"
    ae["AESER"] = ae_raw["IT.AESER"].map({"Yes": "Y", "No": "N"})
    #copia la colonna it.aeacn in una nuova colonna aeacn
    ae["AEACN"] = ae_raw["IT.AEACN"]
    # mappa i valori della colonna it.aerel in una nuova colonna con i valori "NONE", "POSSIBLE", "PROBABLE", "REMOTE"
    ae["AEREL"] = ae_raw["IT.AEREL"].map({"Not Related": "NONE", "Possibly Related": "POSSIBLE", "Probably Related": "PROBABLE", "Remote": "REMOTE"})
    # copia in maiuscolo la colonna it.aeoutcome in una nuova colonna aeout
    ae["AEOUT"] = ae_raw["AEOUTCOME"].str.upper()
    #mappa i valori della colonna aescan in una nuova colonna con i valori "Y" e "N"
    ae["AESCAN"] = ae_raw["AESCAN"].map({"Yes": "Y", "No": "N"})
    # mappa i valori della colonna aescno in una nuova colonna con i valori "Y" e "N"
    ae["AESCONG"] = ae_raw["AESCNO"].map({"Yes": "Y", "No": "N"})
    #mappa i valori della colonna aedis in una nuova colonna con i valori "Y" e "N"
    ae["AESDISAB"] = ae_raw["AEDIS"].map({"Yes": "Y", "No": "N"})
    #mappa i valori della colonna aesod in una nuova colonna con i valori "Y" e "N"
    ae["AESOD"] = ae_raw["AESOD"].map({"Yes": "Y", "No": "N"})
    #mappa i valori della colonna it.aesdth in una nuova colonna con i valori "Y" e "N"
    ae["AESDTH"] = ae_raw["IT.AESDTH"].map({"Yes": "Y", "No": "N"})
    #mappa i valori della colonna it.aeshosp in una nuova colonna con i valori "Y" e "N"
    ae["AESHOSP"] = ae_raw["IT.AESHOSP"].map({"Yes": "Y", "No": "N"})
    #mappa i valori della colonna it.aeslif in una nuova colonna con i valori "Y" e "N"
    ae["AESLIFE"] = ae_raw["IT.AESLIFE"].map({"Yes": "Y", "No": "N"})

    # converte le date in formato ISO 8601 (aaaa-mm-gg) e le assegna alle colonne AEDTC, AESTDTC, AEENDTC
    ae["AEDTC"] = a_iso(ae_raw["AEDTCOL"], "%m/%d/%Y")
    # date parziali (solo anno) restano come nel grezzo, senza inventare mese e giorno
    completa = ae_raw["IT.AESTDAT"].str.len() == 10
    ae["AESTDTC"] = a_iso(ae_raw["IT.AESTDAT"].where(completa), "%m/%d/%Y").fillna(ae_raw["IT.AESTDAT"])
    # controlla se la lunghezza della stringa è 10 (formato completo) e converte solo quelle, lasciando le altre come sono.
    completa = ae_raw["IT.AEENDAT"].str.len() == 10
    ae["AEENDTC"] = a_iso(ae_raw["IT.AEENDAT"].where(completa), "%m/%d/%Y").fillna(ae_raw["IT.AEENDAT"])

    # funzione per calcolare il giorno di studio a partire da una data e dalla RFSTDTC (prima dose)
    def giorno_studio(DMDTC, RFSTDTC):
        """Calcola il giorno di studio a partire da una data e dalla data di screening."""
        giorni = (pd.to_datetime(DMDTC, format="%Y-%m-%d", errors="coerce") - pd.to_datetime(RFSTDTC, format="%Y-%m-%d", errors="coerce")).dt.days
        return giorni.where(giorni < 0, giorni + 1).astype("Int64")

    # RFSTDTC preso da DM per soggetto
    rif = ae["USUBJID"].map(dm.set_index("USUBJID")["RFSTDTC"]) #
    ae["AESTDY"] = giorno_studio(ae["AESTDTC"], rif)
    ae["AEENDY"] = giorno_studio(ae["AEENDTC"], rif)

    # AESEQ: numero progressivo per soggetto, eventi ordinati per data di inizio e termine
    ae = ae.sort_values(["USUBJID", "AESTDTC", "AETERM"], kind="stable")   # 1. ordina
    ae["AESEQ"] = ae.groupby("USUBJID").cumcount() + 1                     # 2. numera
    ae = ae.sort_index()                                                    # 3. rimette l'ordine originale
    return ae

    ae["AESPID"] = None  # AESPID non è richiesto in questo studio, quindi rimane vuoto