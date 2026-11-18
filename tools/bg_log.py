"""Registro anti-ripetizione degli sfondi (ultimi 30). Vedi STRATEGIA.md, sezione Creatività grafica.
Regole: (1) lo stesso concept non può comparire negli ultimi 8 sfondi (circa 2 giorni);
(2) la stessa combinazione concept+variante+layout non può comparire negli ultimi 30.
Uso da riga di comando: python3 bg_log.py  -> stampa gli ultimi 30 sfondi con soggetto, luce, palette, layout."""
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_log.json")
def load():
    return json.load(open(P)) if os.path.exists(P) else []
def check(entries_new):
    log = load(); last30 = log[-30:]; last8 = [e["concept"] for e in log[-8:]]; problems = []
    seen_new = []
    for e in entries_new:
        key = (e["concept"], e.get("variant"), e.get("layout"))
        if e["concept"] in last8: problems.append(f'concept "{e["concept"]}" già usato negli ultimi 8 sfondi')
        if any((x["concept"], x.get("variant"), x.get("layout")) == key for x in last30): problems.append(f"combinazione {key} già usata negli ultimi 30")
        if e["concept"] in seen_new and e.get("group") is None: problems.append(f'concept "{e["concept"]}" ripetuto nello stesso giorno')
        seen_new.append(e["concept"])
    return problems
def append(entries_new):
    log = load() + entries_new; json.dump(log[-200:], open(P, "w"), indent=1, ensure_ascii=False)
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "--registra":
        append(json.load(open(sys.argv[2]))); print("Registrati."); sys.exit()
    for e in load()[-30:]:
        print(f'{e.get("date","")} {e.get("item",""):10} {e["concept"]:11} v{e.get("variant","")} {e.get("layout",""):8} | {e.get("soggetto","")} | {e.get("luce","")} | {e.get("palette","")} | {e.get("composizione","")}')
