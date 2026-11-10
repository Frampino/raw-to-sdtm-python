# Discrepanze QC: dominio DM

| Variabile | Cosa vedo | Perché secondo me | Cosa decido |
|---|---|---|---|
| AESEQ | 578 righe diverse su 1191 | AESEQ deve solo essere unico per soggetto; il riferimento usa una numerazione sua che dal grezzo non si ricava | Tengo la mia regola (ordine per AESTDTC, poi AETERM) e la scrivo nella specifica |
| AESPID | Tutte le righe | Nel grezzo non c'è una colonna da cui prenderlo: probabilmente è il numero di riga del CRF, non esportato | Lascio vuoto; chiedo al data management di includerlo nell'export |
| AELLTCD, AESOCCD | 1182 righe diverse | Il grezzo ha i codici MedDRA, il riferimento li lascia vuoti | Tengo i codici: sono previsti dall'SDTMIG quando si usa MedDRA |
| AESTDTC | 15 righe diverse | Nel grezzo la data è vuota, il riferimento ha anno e mese: viene da una fonte che non abbiamo | Lascio vuoto, non invento date; apro una query al data management |
| AESTDY | 1 riga (01-716-1063) | Evento e prima dose sono lo stesso giorno, quindi la regola dà 1; il 366 del riferimento sembra un errore | Tengo 1 |
