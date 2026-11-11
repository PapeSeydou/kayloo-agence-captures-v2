# KAYLOO voice-over takes, videos 1 and 2, voice Kore

WAV files generated with the same model and the same settings as the approved Video 1 takes.

Updated on 2026-11-11: three revised takes were added, `v1-scene-07-documents-registre`,
`v1-scene-06-fin-ecosysteme` and `v2-scene-02-packs-mobile-money`. The two takes they replace,
`v1-scene-07-documents` and `v2-scene-02-packs`, moved to `_replaced/`. There are now 14 active takes.

## Settings used for every take

| Setting | Value |
|---|---|
| Endpoint | `POST https://openrouter.ai/api/v1/audio/speech` |
| Model | `google/gemini-3.8-flash-tts` |
| Voice | `Kore` |
| response_format | `pcm`, wrapped to WAV 24 kHz mono 16-bit |
| Style prompt | pasted as `instructions`, identical in all 13 calls |
| Post-processing | trim of model silence, 150 ms of silence added at each end, 5 ms fades, peak 0.85 then loudness levelling |

The style prompt, identical character for character in every call:

```
Lis ce texte en français, avec la voix chaleureuse et souriante d'une jeune femme dakaroise,
professionnelle mais complice, comme une amie qui te montre une super appli. Débit vif mais clair,
beaucoup d'énergie positive, jamais criard. Prononce « KAYLOO » comme « Kay-lou ».
```

## Files

Total spoken programme: 99.0 s across 14 active takes.

| File | Duration (s) | Transcript matches | Tries | Remarks |
|---|---|---|---|---|
| v1-scene-02-compte-Kore.wav | 8.74 | yes | 2 (kept 2) | Attempt 1 spoke "short pause" aloud; attempt 2 is clean. Laugh tag produces a real laugh syllable, no spoken word. |
| v1-scene-03-role-Kore.wav | 4.21 | yes | 1 (kept 1) | Clean first try. |
| v1-scene-04-agence-Kore.wav | 6.95 | yes | 1 (kept 1) | Clean first try. |
| v1-scene-07-documents-Kore.wav | 8.58 | yes | 3 (kept 1) | All three attempts are correct audio. Whisper flags it only because it writes the spelled acronyms "NINÉA" and "RCCM" differently from "Ni-né-a" and "R. C. C. M.". Kept attempt 1. Qwen ASR hears "Ninea, RCCM" and "quarante-huit heures". |
| v1-scene-08-valide-Kore.wav | 7.12 | yes | 1 (kept 1) | Clean first try. |
| v2-scene-01-hook-Kore.wav | 2.55 | yes | 3 (kept 3) | Attempt 1 read "excité" aloud. Attempt 2 added words that are not in the script ("Incroyable"). Attempt 3 is clean and is the one kept; it is short (2.55 s) and energetic, as a hook. |
| v2-scene-02-packs-Kore.wav | 8.59 | yes | 1 (kept 1) | Clean first try. "Business" and "Découverte" both heard correctly. |
| v2-scene-03-activation-Kore.wav | 5.03 | yes | 3 (kept 3) | Attempt 1 turned the [excited] tag into an audible gasp. Attempt 2 started "En active". Attempt 3 is clean apart from ASR writing "Un clic" as a question. Kept attempt 3. |
| v2-scene-04-ajout-Kore.wav | 7.86 | yes | 2 (kept 2) | Attempt 1 mangled "Nouveau bien" into "Nouveaux biens" and added "J'en clique"; attempt 2 is clean. |
| v2-scene-05-fiche-Kore.wav | 13.32 | yes | 1 (kept 1) | Clean first try, longest take at 13.32 s. The six-step list is read without the tags being spoken. |
| v2-scene-06-validation-Kore.wav | 5.74 | yes | 1 (kept 1) | Clean first try. |
| v2-scene-07-enligne-Kore.wav | 6.68 | yes | 1 (kept 1) | Clean first try. |
| v2-scene-08-fin-Kore.wav | 6.00 | yes (ASR spelling only) | 3 (kept 1) | Attempt 1 kept. Whisper writes the URL as "kailou.imo" because it turns the spoken word "point" into a dot; Qwen hears "kailo.immo" and, on the isolated phrase, "Kailu point Immo.". Four extra variants of the URL sentence were tested, none changed the audible result, so the wording was left exactly as supplied. |

Transcripts come from `openai/whisper-large-v3`, cross-checked with `qwen/qwen3-asr-1.7b` whenever whisper scored under 0.95.

## Checks

**Pronunciation.** Verified by transcription, not by ear.

| Item | Written in the TTS text | What the ASRs hear | Verdict |
|---|---|---|---|
| KAYLOO | KAYLOO / kayloo | "Kailou", "Kailo", "Kailu" in every take | Consistent with the Video 1 takes, which transcribe the same way |
| NINEA | Ni-né-a | "NINÉA", "Ninea" | Correct |
| RCCM | R. C. C. M. | "RCCM" from both ASRs | Spelled out, correct |
| Web address | kayloo point immo | Qwen: "kailo.immo", and on the isolated phrase "Kailu point Immo." | "point" is spoken; Whisper renders it as a dot |

**Level.** All files are 24 kHz mono, 16-bit, peak between 0.727 and 0.930, no sample at full scale so no clipping. After levelling, active-speech loudness sits between -15.83 and -14.72 dBFS, a 1.12 dB spread. Before levelling the spread was 3.10 dB.

**Start and end.** Every file has about 150 ms of silence at each end. Two files measure a longer lead (0.252 s for v1-scene-02, 0.205 s for v2-scene-08) because the model puts a soft breath before the first syllable; the digital silence itself is still 150 ms. Nothing is cut: the trims only remove the model's own silence.

**Same voice as the approved Video 1 takes.** Same model, same voice id and the same style prompt string as the approved takes. Measured median pitch (autocorrelation): 187.7 Hz averaged over three approved Video 1 takes, 194.2 Hz over four new ones, a 6.5 Hz difference, about 0.6 semitone. One take (v2-scene-05) sits higher at 224 Hz because it reads the six-step list with more energy.

**Tag handling.** Tags were never left spoken in a delivered file. Two were caught and re-generated: "short pause" spoken aloud in v1-scene-02 attempt 1, and "excité" spoken aloud in v2-scene-01 attempt 1. Two tags turned into non-verbal sounds rather than words: the [excited] gasp in v2-scene-03 attempt 1 and the [laughing] in v1-scene-02, which is an actual laugh and was kept.

## Honest limits

- I cannot hear the audio. Everything above is measured or transcribed, not listened to. Please play all 13 once, mainly to judge whether the smile and the energy match the approved takes.
- The word "point" in the URL exists only in the audio, confirmed by Qwen ASR on the isolated phrase. Whisper is not reliable for that word.
- Two takes carry a soft breath before the first syllable. If that bothers the animation, say so and I will re-cut those two with a firmer trim threshold.

## Regenerating

The generator lives in this session's workspace, not in the delivery folder. It calls the endpoint above with one request per take, transcribes each result, and retries up to three times when a tag is spoken or the transcript drifts.

## Update, three revised takes (2026-11-11)

Same model, same voice, same style prompt string, same 150 ms silence and the same loudness target as the
first thirteen, so they drop into the same timeline.

| File | Duration (s) | Transcript matches | Tries | Remarks |
|---|---|---|---|---|
| v1-scene-07-documents-registre-Kore.wav | 9.11 | yes | 1 | Replaces the RCCM wording with "registre de commerce". Both ASRs hear "NINEA, registre de commerce et pièce d'identité" and "quarante-huit heures". |
| v1-scene-06-fin-ecosysteme-Kore.wav | 4.27 | yes | 1 | New closing scene. ASR spells the brand "Kylo" and "Kailo", the usual spelling variance; the words are correct. "point" is spoken, with Whisper writing it as a dot again. |
| v2-scene-02-packs-mobile-money-Kore.wav | 11.47 | yes | 1 | Longer than the earlier packs take (8.59 s) because of the new sentence. Both ASRs hear "mobile money", Qwen verbatim. |

Levels: -14.85, -14.85 and -15.91 dBFS of active speech, peaks 0.868, 0.859 and 0.930, so no clipping and no
drift against the rest of the set.

Files under `_replaced/` are kept for reference only. They are the earlier takes of scene 07 and of scene 02,
superseded by the wording above.

## Update, four re-cut takes (2026-11-11, second batch)

Same model, same voice, same style prompt string, same 150 ms silence and the same loudness target.

| File | Duration (s) | Transcript matches | Tries | Remarks |
|---|---|---|---|---|
| v1-scene-02-compte-code-Kore.wav | 15.10 | yes | 4 | Replaces v1-scene-02-compte. The three attempts that kept [short pause] spoke the tag aloud ("short pause", "short pose", "charte pause"), so the pause tags were removed and the take was generated again without them. [chuckle] was kept: it is not spoken and it produces an audible laugh. Wording unchanged. |
| v1-scene-05b-statut-Kore.wav | 17.70 | yes | 4 | New scene. Three attempts were rejected for inserted words that are not in the script ("Merci", "voiront", "outil"); the fourth is clean. Both ASRs hear "Compte", "Mon profil", "Validation" and "Validation de compte" as written. |
| v2-scene-02-packs-detail-Kore.wav | 23.26 | yes | 6 | Replaces v2-scene-02-packs-mobile-money. One attempt read "Short pause" aloud, one paraphrased the pack list ("Choisissez ensuite Découverte, Standard…"), one was clean but ended up unused after a selection bug. The kept take reads the numbers in order: cinq, dix, trente, deux, cinquante, trois. |
| v2-scene-03-activation-Kore.wav | 5.16 | yes | 1 | Replaces the earlier activation take. "et vos crédits sont prêts" instead of "arrivent". No tag spoken. |

Levels: -14.85, -14.84, -14.86 and -14.85 dBFS of active speech, peaks 0.836, 0.824, 0.889 and 0.899, so no
clipping and no drift against the rest of the set. Every file has 150 ms of digital silence at both ends. The
first take measures 0.25 s of tail by the 0.012 threshold because the laugh decays softly after the last word;
the digital silence itself is still 150 ms.

Tags: [chuckle] did not have to be replaced by [laughing], it is never read aloud. Only the [short pause] tags of
the first take were dropped, because three attempts in a row spoke them.

Moved to `_replaced/` and kept: v1-scene-02-compte-Kore.wav, v2-scene-02-packs-mobile-money-Kore.wav and the
earlier v2-scene-03-activation-Kore.wav (5.03 s).
