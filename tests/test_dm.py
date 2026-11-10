import pandas as pd
import pytest

from src.derive_dm import derive_dm

VARIABILI = [
    "STUDYID", "DOMAIN", "USUBJID", "SUBJID", "SITEID",
    "RFSTDTC", "RFENDTC", "RFXSTDTC", "RFXENDTC", "RFICDTC", "RFPENDTC",
    "DTHDTC", "DTHFL", "DMDTC", "DMDY", "BRTHDTC", "AGE", "AGEU",
    "SEX", "RACE", "ETHNIC", "COUNTRY",
    "ARMCD", "ARM", "ACTARMCD", "ACTARM", "ARMNRS", "ACTARMUD",
]


@pytest.fixture(scope="module")
def confronto():
    leggi = lambda f: pd.read_csv(f, dtype=str)
    mio = derive_dm(leggi("data/raw/dm_raw.csv"), leggi("data/raw/ds_raw.csv"), leggi("data/raw/ec_raw.csv"))
    ref = leggi("data/reference/dm.csv")
    return mio.set_index("USUBJID", drop=False), ref.set_index("USUBJID", drop=False)


def test_stessi_soggetti(confronto):
    mio, ref = confronto
    assert sorted(mio.index) == sorted(ref.index)


@pytest.mark.parametrize("var", VARIABILI)
def test_variabile(confronto, var):
    mio, ref = confronto
    assert var in mio.columns, f"{var} non c'è ancora"
    a = mio[var].reindex(ref.index).astype("string").fillna("")
    b = ref[var].astype("string").fillna("")
    diversi = a != b
    esempi = pd.DataFrame({"mio": a[diversi], "riferimento": b[diversi]}).head(3)
    assert not diversi.any(), f"{var}: {diversi.sum()} soggetti diversi su {len(b)}\n{esempi}"
