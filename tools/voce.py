"""Budget giornaliero ElevenLabs: max 600 caratteri di testo al giorno (ora di Roma).
Uso: python3 tools/voce.py              -> mostra consumo di oggi e residuo
     python3 tools/voce.py check "testo" -> dice se il testo sta nel budget (exit 1 se no)
     python3 tools/voce.py add "testo" uso flow_id  -> registra una generazione GIÀ completata"""
import json, os, sys, datetime
from zoneinfo import ZoneInfo
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elevenlabs_log.json"); LIMIT = 600
def today(): return datetime.datetime.now(ZoneInfo("Europe/Rome")).date().isoformat()
def load(): return json.load(open(P)) if os.path.exists(P) else []
EXTRA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elevenlabs_extra.json")
def limit(d=None):
    """Limite del giorno: 600 + eventuale deroga una tantum autorizzata dal proprietario (elevenlabs_extra.json)."""
    d = d or today(); x = json.load(open(EXTRA)) if os.path.exists(EXTRA) else {}
    return LIMIT + x.get(d, {}).get("extra", 0)
def used(d=None): d = d or today(); return sum(e["chars"] for e in load() if e["date"] == d)
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(f"Oggi {today()}: usati {used()} / {limit()} caratteri, residuo {limit()-used()}"); sys.exit()
    if a[0] == "check":
        n = len(a[1]); ok = used() + n <= limit()
        print(f"Testo {n} caratteri; usati {used()}; dopo {used()+n}/{limit()} -> {'OK' if ok else 'SUPERA IL LIMITE: non generare'}"); sys.exit(0 if ok else 1)
    if a[0] == "add":
        L = load(); L.append(dict(date=today(), chars=len(a[1]), uso=a[2] if len(a) > 2 else "", flow=a[3] if len(a) > 3 else ""))
        json.dump(L, open(P, "w"), indent=1, ensure_ascii=False); print(f"Registrato. Residuo oggi: {limit()-used()}")
