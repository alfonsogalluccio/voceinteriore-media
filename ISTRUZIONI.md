# Manuale operativo – esecuzione quotidiana

Leggere anche STRATEGIA.md. Rispondere sempre all'utente in italiano, in modo semplice e sintetico.

## Dati fissi
- Organizzazione Buffer: `6afb10ef95eeea256eaaf045` (fuso Europe/Rome, piano Free: max 10 post in coda per canale)
- Canali: Instagram `6afb11adece6dfde5fe4ec9a` · TikTok `6afb1233ece6dfde5fe4f23c` · YouTube `6afb125aece6dfde5fe4f3f8`
- Facebook: NON collegato (il piano Free consente 3 canali).
- Repo pubblico media: `alfonsogalluccio/voceinteriore-media` → link file: `https://raw.githubusercontent.com/alfonsogalluccio/voceinteriore-media/main/media/AAAA-MM-GG/<file>`
- Repo privato musica: `alfonsogalluccio/voceinteriore-privato` (cartella `music/`). La musica NON va mai nel repo pubblico (la licenza Pixabay vieta di distribuire i brani da soli).

## Preparazione ambiente
```
pip install --break-system-packages -q librosa
git clone --depth 1 https://github.com/alfonsogalluccio/voceinteriore-media
git clone --depth 1 https://github.com/alfonsogalluccio/voceinteriore-privato
```
Strumenti: `tools/make_day.py SPEC.json OUT_DIR MUSIC_DIR` crea tutto (immagini, storie, video, anteprima).
Se nella cartella musica ci sono brani nuovi non presenti in `tools/music_library.json`, rigenerarla con
`python3 tools/music_lib.py MUSIC_DIR tools/music_library.json`.

## Formato SPEC.json
```json
{"date":"2026-11-18","palette":"notte","seed":11,
 "post":{"kicker":"Parola per oggi","text":"...","sub":"Isaia 41,10"},
 "carousel":[{"kicker":"...","text":"...","numbered":false}, {"text":"...","sub":"Salmo 23,1"}],
 "stories":[{"kicker":"Buongiorno","text":"...","note":"Invialo a chi ami"},{"kicker":"Domanda della sera","text":"...","palette":"viola"}],
 "reel":{"dur":12,"music":"<file della libreria>","cuts":[3.3,8.2],
   "scenes":[{"style":"hook","text":"...","instant":true},
             {"style":"verse","kicker":"Dio ti dice","text":"«...»","sub":"Riferimento"},
             {"style":"hook","text":"...","small":"invito all'azione"}]}}
```
Usare `post` OPPURE `carousel`. Andare a capo con `\n` per evitare parole isolate su una riga. Palette: alba, notte, oro, mare, viola. Cambiare `seed` ogni giorno.

## Scelta della musica
`tools/music_library.json` contiene per ogni brano: umore (emozionale / luminoso / epico), bpm, miglior estratto.
Scegliere il brano adatto al tema; non usare lo stesso brano due giorni di fila (controllare CONTENT_LOG.md).
Ammessi solo brani con licenza verificata: quelli Pixabay della libreria. Esclusi sempre: brani di artisti famosi (es. Einaudi), canzoni commerciali, file di origine sconosciuta.

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

## Registro
Aggiungere una riga a CONTENT_LOG.md per ogni giornata (data, tema, format, versetti, brano, palette) e fare push.

## Controllo pubblicazioni
Con `list_posts` (status sent / error) verificare le ultime 24 ore. Per ogni errore: leggere il messaggio, correggere (link, formato, testo) e riprogrammare. Se non risolvibile, segnalarlo all'utente con il motivo esatto.
