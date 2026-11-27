# Bozze Reel FORTE con la "divisa" (preparate il 23/11/2026)

Tre Reel pronti da produrre nei prossimi giorni, uno al giorno, al posto di un Reel normale. Seguono le regole di STRATEGIA.md, sezione 11, "Divisa FORTE e protagonista anonimo".
- Voce ufficiale ElevenLabs, sempre sotto i 600 caratteri del giorno: controllare prima con `python3 tools/voce.py check "…"`.
- Durata prevista 35-45 s.
- Per tutti e tre: `"particles": false`, `"grade": "bn"`, prima scena con il riferimento in `impact` oro, poi scene `"style": "caption"` che seguono la voce. Ultima scena: «Alzati. Dio non ha finito con te.»
- I tagli (`cuts`) vanno allineati alla voce generata: ascoltarla e mettere un taglio alla fine di ogni frase.
- Annotare in CONTENT_LOG.md come "Esperimento: divisa FORTE".

---

## 1. Serie "Alzati" – Parte 1 · Proverbi 24,16 — **usata il 2026-11-24**
- Note d'uso: voce 471 caratteri con tag (28,3 s + 4,6 s di pause aggiunte = Reel 36 s); clip rallentata 1,4x con `"pingpong": true`; didascalia della bozza sostituita ("Sette volte a terra. Otto volte in piedi." ricalca un proverbio famoso) con "Non conto le cadute. Conto le volte che mi ha rialzato."
- **Clip:** `clips/uomo-cappuccio-lago-nuvole.mp4` (darken 0,3).
- **Testo CEI:** verificato su CEI 2008: «perché se il giusto cade sette volte, egli si rialza».
- **Voce (372 caratteri):**
  > Proverbi 24,16. «Se il giusto cade sette volte, egli si rialza.» Non dice che non cadrai. Dice che ti rialzerai. Sono caduto anch'io: nel lavoro, nelle parole sbagliate, nella paura di non farcela. E ogni volta che ero a terra, Dio era lì, più vicino di quanto pensassi. Allora oggi non conto le cadute. Conto le volte che mi ha rialzato. Alzati. Dio non ha finito con te.
- **Scene a schermo:**
  1. `*PROVERBI 24,16*`
  2. Se il giusto cade sette volte,
  3. egli si rialza.
  4. Non dice che non cadrai.
  5. Dice che ti rialzerai.
  6. Oggi non conto le cadute.
  7. Conto le volte che mi ha rialzato.
  8. Alzati. Dio non ha finito con te.
- **Didascalia:** "Sette volte a terra. Otto volte in piedi." + riga vuota + "Invialo a chi oggi è a terra 🤍" + i 5 hashtag fissi.

## 2. "Per chi combatte" · Salmo 23,4 — **usata il 2026-11-26** (come carosello IG 3 slide e TikTok 6 immagini, senza Reel né voce per la sezione 12)
- **Clip:** `clips/persona-strada-notte.mp4` (darken 0,25).
- **Testo CEI:** «Anche se vado per una valle oscura, non temo alcun male, perché tu sei con me». Riverificare su bibbiaedu.it prima di produrre.
- **Voce (358 caratteri):**
  > Salmo 23,4. «Anche se vado per una valle oscura, non temo alcun male, perché tu sei con me.» Il salmo non promette che non ci saranno valli oscure. Promette che non le attraverserai da solo. C'è chi stanotte è in una corsia d'ospedale, chi aspetta una telefonata, chi non dorme per un figlio. Se sei tu, ascolta: il buio è vero. Ma lui è più vicino del buio.
- **Scene a schermo:**
  1. `*SALMO 23,4*`
  2. Anche se vado per una valle oscura,
  3. non temo alcun male,
  4. perché tu sei con me.
  5. Non promette che non ci saranno valli oscure.
  6. Promette che non le attraverserai da solo.
  7. Il buio è vero. Ma lui è più vicino del buio.
  8. Alzati. Dio non ha finito con te.
- **Didascalia:** "Non da solo." + riga vuota + "Scrivi il nome di chi sta attraversando la sua valle 🙏" + i 5 hashtag fissi.

## 3. "Verità che fa bene" · Romani 8,31 — **usata il 2026-11-28**
- Note d'uso: voce 484 caratteri con tag (30,2 s, Reel 36 s) con la chiusura «Alzati. Dio non ha finito con te.» aggiunta alla voce; clip `uomo-vetta-braccia-alba` solo nei primi 9 s (`"clip_end": 9`: dopo 9,5 s si vede il volto di profilo), rallentata 1,4x avanti-indietro; scene a schermo più fitte (13) per seguire la voce.
- **Clip:** ~~`clips/uomo-collina-tramonto-silhouette.mp4`~~ usata il 26/11 nel TikTok (regola delle 3 settimane): usare `clips/uomo-vetta-braccia-alba.mp4` oppure `clips/uomo-terrazza-mare-nuvole.mp4` (darken 0,3). Nota del 26/11 sera.
- **Testo CEI:** «Se Dio è per noi, chi sarà contro di noi?». Riverificare su bibbiaedu.it prima di produrre.
- **Voce (349 caratteri):**
  > Romani 8,31. «Se Dio è per noi, chi sarà contro di noi?» Lo diciamo facilmente, in chiesa, quando va tutto bene. Poi arriva la lettera che non volevi, la diagnosi, la porta che si chiude. E lo dimentichiamo. Ma questa frase non è stata scritta per i giorni facili. È stata scritta per oggi. Per te. Chi è contro di te non ha l'ultima parola. Dio sì.
- **Scene a schermo:**
  1. `*ROMANI 8,31*`
  2. Se Dio è per noi,
  3. chi sarà contro di noi?
  4. Non è stata scritta per i giorni facili.
  5. È stata scritta per oggi. Per te.
  6. L'ultima parola è di Dio.
  7. Alzati. Dio non ha finito con te.
- **Didascalia:** "Non per i giorni facili." + riga vuota + "Salvalo per il giorno in cui avrai paura 🔖" + i 5 hashtag fissi.

---
**Hashtag fissi (proposta):** #fedecristiana #paroladidio #preghiera #gesù #dio (+1 a tema, per esempio #salmo23).

**Nota tecnica (24/11):** nel Reel con la voce mettere `"snap_beats": false` (altrimenti i tagli si spostano sui beat della musica e i sottotitoli non seguono la voce) e, per clip più corte del video, `"slow": 1.3-1.5` e `"pingpong": true` nel `bg`. Su Instagram usare solo i 5 hashtag fissi (limite di 5); il sesto a tema va su TikTok e YouTube.

---
## Bozze nuove (scritte il 27/11/2026, stesse regole della divisa)

## 4. Serie "Alzati" – Parte 2 · Pietro (Giovanni 21,17)
- **Clip:** una tra `uomo-pontile-alba`, `uomo-cammina-pontile-nebbia`, `persona-riva-torrente-montagna` (darken 0,3; verificare che non si veda il volto).
- **Testo CEI:** «Signore, tu conosci tutto; tu sai che ti voglio bene» (Gv 21,17). Verificare parola per parola prima di produrre.
- **Voce (bozza, circa 400 caratteri con tag):**
  > Giovanni 21,17. «Signore, tu conosci tutto; tu sai che ti voglio bene.» Pietro aveva detto tre volte: non lo conosco. Tre volte. E Gesù non gli chiede di spiegare. Gli chiede soltanto: mi vuoi bene? Forse anche tu pensi di averlo deluso troppe volte. Ascolta: il tuo errore non è la fine della tua storia con Lui. Alzati. Dio non ha finito con te.
- **Scene a schermo:** `*GIOVANNI 21,17*` · Signore, tu conosci tutto; · tu sai che ti voglio bene. · Pietro aveva detto tre volte: non lo conosco. · E Gesù non gli chiede di spiegare. · Gli chiede soltanto: mi vuoi bene? · Il tuo errore non è la fine della tua storia con Lui. · Alzati. Dio non ha finito con te.
- **Didascalia:** "Tre volte a terra. Tre volte amato." + "Invialo a chi pensa di aver deluso Dio 🤍" + 5 hashtag fissi.

## 5. "Per chi combatte" · Isaia 41,10 (per chi ha perso il lavoro)
- **Clip:** `uomo-casa-diroccata-albero` oppure `uomo-albero-solitario-alba` (darken 0,3).
- **Testo CEI:** «Non temere, perché io sono con te; non smarrirti, perché io sono il tuo Dio» (Is 41,10, prima parte). Verificare prima di produrre. Nota: Is 41,10 usato il 17/11 in un altro format (più di 4 settimane prima va bene).
- **Voce (bozza, circa 420 caratteri con tag):**
  > Isaia 41,10. «Non temere, perché io sono con te; non smarrirti, perché io sono il tuo Dio.» Questo è per te che stamattina non hai un posto dove andare. Per te che hai mandato l'ennesimo curriculum e nessuno ha risposto. Il tuo valore non l'ha deciso chi ti ha lasciato a casa. L'ha deciso Dio. E Lui non ti ha licenziato. Alzati. Dio non ha finito con te.
- **Scene a schermo:** `*ISAIA 41,10*` · Non temere, perché io sono con te; · non smarrirti, perché io sono il tuo Dio. · Per te che stamattina non hai un posto dove andare. · Il tuo valore non l'ha deciso chi ti ha lasciato a casa. · L'ha deciso Dio. · Alzati. Dio non ha finito con te.
- **Didascalia:** "Il tuo valore non l'ha deciso un colloquio." + "Invialo a chi sta cercando lavoro 🙏" + 5 hashtag fissi.
