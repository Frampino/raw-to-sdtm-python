import pandas as pd
import pytest

from src.derive_ae import derive_ae

VARIABILI = [
    "STUDYID", "DOMAIN", "USUBJID", "AESEQ", "AESPID", "AETERM",
    "AELLT", "AELLTCD", "AEDECOD", "AEPTCD", "AEHLT", "AEHLTCD", "AEHLGT", "AEHLGTCD",
    "AEBODSYS", "AEBDSYCD", "AESOC", "AESOCCD",
    "AESEV", "AESER", "AEACN", "AEREL", "AEOUT",
    "AESCAN", "AESCONG", "AESDISAB", "AESDTH", "AESHOSP", "AESLIFE", "AESOD",
    "AEDTC", "AESTDTC", "AEENDTC", "AESTDY", "AEENDY",
]


@pytest.fixture(scope="module")
def confronto():
    leggi = lambda f: pd.read_csv(f, dtype=str)
    dm = leggi("data/reference/dm.csv")  # serve RFSTDTC per AESTDY e AEENDY
    mio = derive_ae(leggi("data/raw/ae_raw.csv"), dm)
    ref = leggi("data/reference/ae.csv")
    # le righe del riferimento sono nello stesso ordine del grezzo: si confrontano per posizione
    return mio.reset_index(drop=True), ref.reset_index(drop=True)


def test_stesse_righe(confronto):
    mio, ref = confronto
    assert len(mio) == len(ref)


@pytest.mark.parametrize("var", VARIABILI)
def test_variabile(confronto, var):
    mio, ref = confronto
    assert var in mio.columns, f"{var} non c'è ancora"
    a = mio[var].astype("string").fillna("")
    b = ref[var].astype("string").fillna("")
    diversi = a != b
    esempi = pd.DataFrame({"USUBJID": ref["USUBJID"][diversi], "mio": a[diversi], "riferimento": b[diversi]}).head(3)
    assert not diversi.any(), f"{var}: {diversi.sum()} righe diverse su {len(b)}\n{esempi}"
