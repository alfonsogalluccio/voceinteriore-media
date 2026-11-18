# Manuale operativo – esecuzione quotidiana

Leggere anche STRATEGIA.md. Rispondere sempre all'utente in italiano, in modo semplice e sintetico.

## Dati fissi
- Organizzazione Buffer: `6afb10ef95eeea256eaaf045` (fuso Europe/Rome, piano Free: max 10 post in coda per canale)
- Canali: Instagram `6afb11adece6dfde5fe4ec9a` · TikTok `6afb1233ece6dfde5fe4f23c` · YouTube `6afb125aece6dfde5fe4f3f8`
- Facebook: NON collegato (il piano Free consente 3 canali).
- Repo pubblico media: `alfonsogalluccio/voceinteriore-media` → link file: `https://raw.githubusercontent.com/alfonsogalluccio/voceinteriore-media/main/media/AAAA-MM-GG/<file>`
- Musica principale: cartella `music/` di QUESTO repo, con i soli brani `proprio-*` creati dal proprietario (uso libero, messi qui il 18/11 perché le attività programmate non raggiungono il repo privato).
- Repo privato musica: `alfonsogalluccio/voceinteriore-privato` (cartella `music/`) con i brani Pixabay: usarlo solo se raggiungibile. I brani Pixabay NON vanno mai nel repo pubblico (la licenza vieta di distribuirli da soli).

## Preparazione ambiente
```
pip install --break-system-packages -q librosa
git clone --depth 1 https://github.com/alfonsogalluccio/voceinteriore-media
git clone --depth 1 https://github.com/alfonsogalluccio/voceinteriore-privato   # facoltativo: se fallisce, usare music/ di questo repo
```
MUSIC_DIR = `music/` di voceinteriore-media (brani propri). Se il repo privato è raggiungibile, si possono usare anche i brani Pixabay da lì.
Strumenti: `tools/make_day.py SPEC.json OUT_DIR MUSIC_DIR` crea tutto (immagini, storie, video, anteprima).
Se nella cartella musica ci sono brani nuovi non presenti in `tools/music_library.json`, rigenerarla con
`python3 tools/music_lib.py MUSIC_DIR tools/music_library.json`.

## Formato SPEC.json
```json
{"date":"2026-11-19","seed":19,
 "carousel_style":{"bg":{"concept":"carta","variant":1},"layout":"sinistra","font":"serif"},
 "carousel":[{"kicker":"...","text":"...","numbered":false,"note":"Scorri"}, {"text":"...","sub":"Salmo 23,1"}],
 "stories":[{"kicker":"Buongiorno","text":"...","note":"Invialo a chi ami","bg":{"concept":"finestra","variant":0},"layout":"alto"},
            {"kicker":"Domanda della sera","text":"...","bg":{"concept":"stelle","variant":2},"layout":"basso","font":"sans"}],
 "reel":{"dur":12,"music":"<file della libreria>","cuts":[3.3,8.2],"bg":{"concept":"mare","variant":0},
   "scenes":[{"style":"hook","text":"...","instant":true},
             {"style":"verse","kicker":"Dio ti dice","text":"«...»","sub":"Riferimento"},
             {"style":"hook","text":"...","small":"invito all'azione"}]}}
```
- `post` (oggetto singolo, stessi campi di una slide) OPPURE `carousel`.
- **Sfondi** (`bg`): concept disponibili in `tools/scenes.py` → candela, finestra, montagne, mare, bosco, stelle, citta, pioggia, acquerello, carta, colore (5 varianti), lago, grano, croce, sentiero, cielo (vecchio stile, con `palette`). Ogni concept ha 3 varianti (`variant` 0-2) con colori e composizioni diverse. Foto vere: `{"photo":"backgrounds/<file>.jpg","meta":{...}}`.
- **Layout**: centro, alto, basso, sinistra, grande. **Font**: serif_i, serif, sans. `frame`: true/false.
- Andare a capo con `\n` per evitare parole isolate. Cambiare `seed` ogni giorno.

## Video reali (cartella clips/)
- `clips/catalogo.json` elenca i video veri (Pexels, uso libero) già tagliati in verticale 1080x1920, senza audio, con soggetto, luce, palette e durata.
- Reel/Short/TikTok: `"bg": {"clip": "clips/<nome>.mp4"}` → il video scorre come sfondo (preferire clip lunghe almeno quanto il video; quelle corte vanno in loop). `darken` regola la velatura (default 0.38).
- Storie e post: `"bg": {"clip": "clips/<nome>.mp4", "frame_t": 3.0}` usa un fotogramma come foto (senza frame_t usa il poster).
- Alternare video reali e concept generati: almeno 1 contenuto al giorno con video/foto reale, quando disponibili. Mai la stessa clip prima di 3 settimane.
- Nuovi video dal proprietario: materiale suo, con licenza libera (Pexels, Pixabay, Mixkit) o per cui il proprietario dichiara l'autorizzazione (annotarlo in "fonte"). Scartare sempre video con persone famose o scene di film/serie, marchi, scritte o filigrane.

## Voce narrante ElevenLabs (connettore ElevenCreative)
- **Limite: 600 caratteri di testo al giorno** (ora di Roma), da 0 a 600, mai di più. Registro: `tools/elevenlabs_log.json`. Prima di generare: `python3 tools/voce.py check "TESTO"`; se supera, accorciare o rinunciare. Mai usare crediti oltre il limite senza permesso del proprietario.
- Generazione: `creative_generate_speech` con `model_id: "eleven_v4"`, `generations_count: 1`, voce `VZOd9FMXDnXRZpGn0thg` (Daniela) o `jMEwEYrOKjM6NDQNodla` (Elian). **Mai ripetere una chiamata per riprovare** (consuma di nuovo).
- Attendere con `creative_get_flow_run_status` fino a completed; solo allora registrare: `python3 tools/voce.py add "TESTO" "uso" FLOW_ID`.
- Scaricare l'mp3 dal `content_url` e passarlo al video con `"voice": "<percorso mp3>"` nel reel (opzioni `voice_delay`, `music_vol_with_voice`). Il testo a schermo deve seguire ciò che la voce dice.
- Se il download è bloccato (dominio elevenlabsusercontent.com non consentito), non generare altro: pubblicare il video senza voce e segnalarlo all'utente.
- Nel messaggio finale indicare sempre: caratteri usati oggi e residuo (o "non verificabile", senza inventare).
- Testo per la voce: italiano naturale, frasi brevi, niente emoji né hashtag; versetti CEI esatti.

## Procedura sfondi (obbligatoria)
1. `python3 tools/bg_log.py` → leggere gli ultimi 30 sfondi e scegliere concept, variante e layout nuovi (vedi STRATEGIA.md, sezione 1).
2. `make_day.py` si ferma con "RIPETIZIONE VISIVA" se si ripete: cambiare e rigenerare (forzare solo con `allow_repeat` + `repeat_reason`).
3. Dopo il controllo qualità: `python3 tools/bg_log.py --registra OUT_DIR/bg_entries.json`, poi commit di `tools/bg_log.json`.

## Scelta della musica
`tools/music_library.json` contiene per ogni brano: umore (emozionale / luminoso / epico), bpm, miglior estratto.
Scegliere il brano adatto al tema; non usare lo stesso brano due giorni di fila (controllare CONTENT_LOG.md).
Ammessi solo i brani della libreria: Pixabay (licenza verificata) e i brani `proprio-*` creati dal proprietario (uso libero). Preferire spesso i brani propri: sono unici e riconoscibili. Esclusi sempre: brani di artisti famosi (es. Einaudi), canzoni commerciali, file di origine sconosciuta.

## Controllo qualità (obbligatorio, guardare davvero le immagini)
1. Aprire `preview.jpg` e i `_frame_*.jpg` con lo strumento Read: testo leggibile, nessuna parola isolata o tagliata, niente sovrapposizioni, primo fotogramma del video con testo visibile.
2. Ortografia e grammatica italiane perfette; accenti corretti (perché, è, più).
3. Versetti: verificati parola per parola sul testo CEI 2008 con una ricerca web; riferimento giusto.
4. Video: durata 10–15 s, 1080x1920, audio presente (ffprobe), volume corretto.
5. Se qualcosa non va: correggere e rigenerare. Mai pubblicare contenuti approssimativi.

## Pubblicazione su Buffer
- Caricare i file in `media/AAAA-MM-GG/` del repo pubblico, fare push, verificare che ogni link risponda 200.
- Creare i post con `create_post`, `schedulingType: automatic`, `mode: customScheduled`, `dueAt` con offset +01:00 (inverno) / +02:00 (estate).
- Instagram post: `metadata.instagram {type:"post", shouldShareToFeed:true}`; carosello = più immagini nello stesso post.
- Storie: `{type:"story", shouldShareToFeed:false}`.
- Reel: `{type:"reel", shouldShareToFeed:true}` + `thumbnailOffset` (ms) su un fotogramma con testo.
- TikTok: `metadata.tiktok {isAiGenerated:true}`.
- YouTube: `metadata.youtube {title (max 100 caratteri, con #shorts), categoryId:"22", privacy:"public", madeForKids:false, isAiGenerated:true}`.
- Fare le chiamate a Buffer una alla volta, non in parallelo.
- Orari sperimentali di partenza (Roma): Storia 1 08:00 · Reel IG 13:00 · Short YT 18:00 · Post IG 19:30 · TikTok 20:30 · Storia 2 21:00. Aggiornare in base ai report.

## Ricerca
Ogni giorno annotare in TENDENZE.md almeno 1 osservazione utile trovata sul web (con fonte), indicando se è dato verificato o ipotesi e se passa il filtro "per noi".

## Registro
Aggiungere una riga a CONTENT_LOG.md per ogni giornata (data, tema, format, versetti, brano, concept grafici e layout, eventuale esperimento) e fare push.

## Controllo pubblicazioni
Con `list_posts` (status sent / error) verificare le ultime 24 ore. Per ogni errore: leggere il messaggio, correggere (link, formato, testo) e riprogrammare. Se non risolvibile, segnalarlo all'utente con il motivo esatto.
