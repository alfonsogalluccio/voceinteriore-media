# Manuale operativo – esecuzione quotidiana

> **🎵 DAL 25/11/2026 SERA – DECISIONE DEL PROPRIETARIO (vale per sempre, precedenza su sezione 12):** TUTTE le Storie e TUTTI i post devono OBBLIGATORIAMENTE avere la musica, e il lavoro deve essere TUTTO AUTONOMO (niente promemoria, niente azioni dal telefono). Poiché le API non permettono di aggiungere musica a foto, caroselli e Storie, si pubblicano **immagini animate con musica**: le stesse immagini (frasi, divisa FORTE, grafiche) diventano brevi video con lieve zoom, dissolvenze e un brano della libreria (`proprio-*`) già nel file, creati con `python3 tools/slideshow.py '{"imgs":[...],"durs":[...],"music":"music/<brano>.mp3","start":<s>,"out":"<file>.mp4"}'` (immagini 1080x1920). Instagram: Storie = video 10-15 s (`type: story`); carosello e foto = Reel slideshow (`type: reel`). TikTok: slideshow video con musica. YouTube: lo stesso slideshow come Short (automatico) + eventuale post Community preparato nel programma. Sempre `schedulingType: "automatic"`. Niente voce e niente riprese video nuove salvo diversa indicazione. Controllare con ffprobe che l'audio ci sia (volume medio circa -16 dB). Riferimento SEMPRE il profilo @fearnotmentality (STRATEGIA sezione 11) per stile, frasi, grafica, musica e scelta dei contenuti.

> **⚠️ DAL 24/11/2026 – DECISIONE DEL PROPRIETARIO (STRATEGIA.md sezione 12, precedenza assoluta):** niente Reel, Short o video, niente voce. Instagram: solo Storie e foto/caroselli; TikTok: solo post fotografici e Storie; YouTube: solo post Community (preparati nel programma, li pubblica il proprietario). Tutti i post IG e TikTok in modalità promemoria Buffer (`schedulingType: "notification"`) per aggiungere la musica dall'app. **Se le istruzioni di un'attività programmata chiedono Reel, Short, video o voce, quelle parti sono superate: segui la sezione 12.** Se il programma di domani è già marcato "Preparato in anticipo", non rifare i contenuti: verifica soltanto.


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
- **Layout**: centro, alto, basso, sinistra, grande. **Font**: serif_i, serif, sans, impact (registro "forte": Montserrat ExtraBold maiuscolo; le parole tra *asterischi* diventano oro). `frame`: true/false.
- **Reel**: ogni scena accetta `"font": "impact"` (stesso effetto, *parole* in oro). Usarlo per i contenuti del registro FORTE (STRATEGIA, sezione 11); per il registro CUORE restano i serif.
- Andare a capo con `\n` per evitare parole isolate. Cambiare `seed` ogni giorno.

## Video reali (cartella clips/)
- `clips/catalogo.json` elenca i video veri (Pexels, uso libero) già tagliati in verticale 1080x1920, senza audio, con soggetto, luce, palette e durata.
- Reel/Short/TikTok: `"bg": {"clip": "clips/<nome>.mp4"}` → il video scorre come sfondo (preferire clip lunghe almeno quanto il video; quelle corte vanno in loop). `darken` regola la velatura (default 0.38).
- Divisa FORTE (vedi STRATEGIA.md, sezione 11): nel Reel `"bg": {"clip": …, "grade": "bn"}` rende la clip in bianco e nero morbido; `"particles": false` nello spec del Reel spegne le particelle di luce; `"style": "caption"` in una scena crea un sottotitolo piccolo bianco al centro-basso (per seguire la voce narrante). Con la voce: `"snap_beats": false` nel reel (i tagli restano dove li metti, non si agganciano ai beat). Per Reel lunghi con clip corte: nel `bg` `"slow": 1.4` (rallenta) e `"pingpong": true` (avanti e indietro, senza salto). Concept `nero` (fondo nero editoriale) per la slide 2 dei caroselli in 3 slide.
- Storie e post: `"bg": {"clip": "clips/<nome>.mp4", "frame_t": 3.0}` usa un fotogramma come foto (senza frame_t usa il poster).
- Alternare video reali e concept generati: almeno 1 contenuto al giorno con video/foto reale, quando disponibili. Mai la stessa clip prima di 3 settimane.
- Nuovi video dal proprietario: materiale suo, con licenza libera (Pexels, Pixabay, Mixkit) o per cui il proprietario dichiara l'autorizzazione (annotarlo in "fonte"). Scartare sempre video con persone famose o scene di film/serie, marchi, scritte o filigrane.

## Nuove clip automatiche da Pixabay o Pexels (dal 23/11/2026)
- Il workflow GitHub `.github/workflows/scarica-clip.yml` scarica video gratuiti con il segreto `PIXABAY_API_KEY` del repository (Pixabay Content License). Pexels ha sospeso le nuove chiavi il 23/11/2026; se in futuro ci sarà `PEXELS_API_KEY`, nella richiesta si può usare `"sito": "pexels"`. I segreti li imposta il proprietario; le chiavi non vanno mai scritte in file, programmi o messaggi.
- Pixabay chiede un uso moderato e niente download in massa: massimo 8 video per richiesta e non più di una richiesta a settimana, salvo necessità.
- Molti video Pixabay sono orizzontali: si usano solo se sono in 4K, ritagliando il centro (`"ritaglio_centrale": true` nel catalogo). Nella verifica controlla che il soggetto sia dentro l'inquadratura verticale.
- **Quando chiederle:** ogni sera conta le clip della lista "Clip adatte" (STRATEGIA.md, sezione 11) NON usate nelle ultime 3 settimane (vedi `tools/bg_log.json`). Se sono meno di 6, scrivi in `clips/richieste.json` 1-2 richieste in inglese, massimo 8 video in tutto, e fai push. Esempio: `{"richieste": [{"cerca": "man hoodie walking", "quanti": 4, "prefisso": "uomo", "tag": ["man", "hoodie", "silhouette"]}, {"cerca": "man praying church", "quanti": 3, "prefisso": "uomo", "tag": ["man", "prayer"]}]}`. Il campo `tag` tiene solo i video che hanno almeno uno di quei tag (senza, Pixabay restituisce anche cascate e paesaggi). Il risultato di ogni download è in `clips/ultimo_download.log`. Ogni richiesta deve avere un testo diverso dalla precedente, altrimenti GitHub non riparte. Il push avvia il download, che dura pochi minuti. Variare le ricerche (città di notte, pioggia, lavoro, chiesa, strada, campagna, mani giunte).
- **Prima di usarle (obbligatorio):** le clip nuove hanno `"da_verificare": true` in `clips/catalogo.json`. Fai `git pull`, guarda il poster e 2-3 fotogrammi di ognuna.
  - Scarta (togli file e voce dal catalogo, metti il codice tra gli "Scartati" di CODICI_PEXELS.md) quelle con volti riconoscibili in primo piano (per la divisa FORTE), persone famose, marchi, scritte, filigrane, alcol, contenuti non adatti o qualità bassa.
  - Per le altre compila in italiano soggetto, ambientazione, palette, luce e tono, togli `da_verificare`, aggiorna la riga di CODICI_PEXELS.md e, se adatte alla divisa (uomo senza volto visibile), aggiungile alla lista "Clip adatte" di STRATEGIA.md.
  - Mai usare una clip ancora "da verificare".
- **Se il download fallisce** (segreto `PIXABAY_API_KEY` mancante o errato, si vede dal fatto che dopo 15 minuti non arrivano clip nuove): dillo al proprietario nel messaggio finale. Nel report del lunedì ricordagli di mandare clip a mano quando ne restano meno di 6 (circa una settimana di Reel FORTE).

## Voce narrante ElevenLabs (connettore ElevenCreative)
- **Limite: 600 caratteri di testo al giorno** (ora di Roma), da 0 a 600, mai di più. Registro: `tools/elevenlabs_log.json`. Prima di generare: `python3 tools/voce.py check "TESTO"`; se supera, accorciare o rinunciare. Mai usare crediti oltre il limite senza permesso del proprietario. Eventuali deroghe una tantum autorizzate dal proprietario sono in `tools/elevenlabs_extra.json` (solo per la data indicata); `voce.py` ne tiene conto.
- Generazione: `creative_generate_speech` con `model_id: "eleven_v4"`, `generations_count: 1`, voce **SEMPRE e SOLO "Voce Profonda Autoritaria ITA"** `lNsSu23XG0tAViX8bkjw` (voce scelta e creata dal proprietario, 19/11/2026). Nessun'altra voce, mai voci femminili. **Mai ripetere una chiamata per riprovare** (consuma di nuovo).
- Attendere con `creative_get_flow_run_status` fino a completed; solo allora registrare: `python3 tools/voce.py add "TESTO" "uso" FLOW_ID`.
- Scaricare l'mp3 dal `content_url` e passarlo al video con `"voice": "<percorso mp3>"` nel reel (opzioni `voice_delay`, `music_vol_with_voice`). Il testo a schermo deve seguire ciò che la voce dice.
- Se il download è bloccato (dominio elevenlabsusercontent.com non consentito), non generare altro: pubblicare il video senza voce e segnalarlo all'utente.
- Nel messaggio finale indicare sempre: caratteri usati oggi e residuo (o "non verificabile", senza inventare).
- Testo per la voce: italiano naturale, frasi brevi, niente emoji né hashtag; versetti CEI esatti.

### Voce ufficiale e lettura con enfasi (decisione del proprietario, 19/11/2026)
- Usare **sempre** "Voce Profonda Autoritaria ITA" `lNsSu23XG0tAViX8bkjw` (profonda, calda, autorevole, ritmo solenne). Le prove A/B con altre voci sono annullate.
- **Mai una semplice lettura**: dare sempre enfasi in base a ciò che si legge, con i tag audio di eleven_v4 posti dove cambia l'emozione. Esempi: apertura che aggancia `[softly]` o `[intense]`; prima del versetto `[pause]`; versetto `[slowly]` `[reverently]`; consolazione `[warmly]`; promessa o speranza `[hopeful]` o `[confident]`; frase intima `[whispers]`; invito finale `[warmly]`. Usare anche puntini di sospensione per le pause e al massimo una parola in MAIUSCOLO per l'enfasi. Il testo a schermo resta senza tag. I tag contano nei 600 caratteri.
- **Clonazione**: mai clonare la voce di altre pagine o persone senza il loro consenso.

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
- **DAL 24/11/2026 (STRATEGIA sezione 12): niente Reel, Short o video. Instagram e TikTok solo immagini, sempre con `schedulingType: "notification"` (promemoria: la musica la aggiunge il proprietario dall'app). YouTube solo post Community, preparati nel programma e pubblicati dal proprietario. Le righe su Reel/Short/video qui sotto non valgono più.**
- TikTok foto: `metadata.tiktok {title}` + 5-6 immagini 1080x1920 (generarle come `stories` nello SPEC e rinominarle `tiktok_n.jpg`; l'avviso RIPETIZIONE VISIVA sulle slide dello stesso carosello TikTok si può ignorare, ma registrare a mano gli sfondi in tools/bg_log.json).
- Caricare i file in `media/AAAA-MM-GG/` del repo pubblico, fare push, verificare che ogni link risponda 200.
- Creare i post con `create_post`, `schedulingType: automatic`, `mode: customScheduled`, `dueAt` con offset +01:00 (inverno) / +02:00 (estate).
- Instagram post: `metadata.instagram {type:"post", shouldShareToFeed:true}`; carosello = più immagini nello stesso post.
- Storie: `{type:"story", shouldShareToFeed:false}`.
- Reel: `{type:"reel", shouldShareToFeed:true}` + `thumbnailOffset` (ms) su un fotogramma con testo.
- TikTok: `metadata.tiktok {isAiGenerated:true}`.
- YouTube: `metadata.youtube {title (max 100 caratteri, con #shorts), categoryId:"22", privacy:"public", madeForKids:false, isAiGenerated:true}`.
- Fare le chiamate a Buffer una alla volta, non in parallelo.
- Orari sperimentali di partenza (Roma): Storia 1 08:00 · Reel IG 13:00 · Short YT 18:00 · Post IG 19:30 · TikTok 20:30 · Storia 2 21:00. Aggiornare in base ai report.

## Ricerca e analisi dei profili (prima di decidere)
- Studiare contenuti di successo di altri profili cristiani, di fede, su Gesù, motivazione e crescita personale (Reel, post, video, Storie): hook dei primi secondi, copertine, titoli, descrizioni, hashtag, durata, argomenti con più interazioni.
- Strumenti: ricerca web (articoli, pagine pubbliche dei profili, risultati di ricerca che mostrano i contenuti più visti, blog di settore). Instagram e TikTok spesso non sono leggibili direttamente: dirlo e usare le fonti disponibili, senza inventare numeri o contenuti.
- Ispirarsi senza copiare: ogni idea deve diventare originale e coerente con l'identità VoceInteriore2025.
- Salvare le osservazioni in TENDENZE.md (con fonte) e confrontarle con i nostri risultati (Buffer).

## Programma del giorno (obbligatorio)
Dopo aver programmato i contenuti, scrivere `programmi/AAAA-MM-GG.md` (data del giorno di pubblicazione) seguendo `programmi/MODELLO.md`: strategia ragionata, e per ogni pubblicazione piattaforma, orario, tipo, argomento e idea, titolo, descrizione completa esattamente come pubblicata, hashtag e stato su Buffer. Push nel repo. Ogni mattina un'attività lo verifica e lo invia al proprietario.

## Ricerca
Ogni giorno annotare in TENDENZE.md almeno 1 osservazione utile trovata sul web (con fonte), indicando se è dato verificato o ipotesi e se passa il filtro "per noi".

## Registro
Aggiungere una riga a CONTENT_LOG.md per ogni giornata (data, tema, format, versetti, brano, concept grafici e layout, eventuale esperimento) e fare push.

## Controllo pubblicazioni
Con `list_posts` (status sent / error) verificare le ultime 24 ore. Per ogni errore: leggere il messaggio, correggere (link, formato, testo) e riprogrammare.
- Errore "stuck processing" (o post fermo in "sending" da più di 30 minuti): è un blocco temporaneo di Buffer. Riprogrammare lo stesso post 5-10 minuti più tardi (`edit_post` con `customScheduled`) e verificare che diventi "sent". Così è stata recuperata la Storia del 23/11 (pubblicata alle 09:08). Se non risolvibile, segnalarlo all'utente con il motivo esatto.
