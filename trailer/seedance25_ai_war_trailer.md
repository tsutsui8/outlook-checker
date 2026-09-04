# 30秒 AI戦争 映画予告編 — Seedance 2.5 プロンプト一式

作品タイトル: **THEY LEARN ― シンギュラリティ・フロント ―**
モデル: ByteDance Seedance 2.5（Higgsfield 経由 / `mode: omni_reference`）
参照画像: 添付5枚（① 病院 ② 覚醒 ③ 兵器工場 ④ 市街戦 ⑤ 司令部）

---

## 1. 30秒構成表（トレーラー3幕構造）

| 時間 | 参照 | 内容 | 音楽・音響の設計 |
|---|---|---|---|
| 0.0–5.0s | ① | 白い病室。ロボットが患者の手を握り、女医が微笑む | ピアノ単音→弦がゆっくり上昇。心電図の穏やかな電子音 |
| 5.0–9.0s | ② | 暗い工場。1体だけが首を上げ、バイザーに光が灯る | 音楽が**断ち切られる**。低域ドローン＋電流ノイズ→BRAAAM 1発 |
| 9.0–14.0s | ③ | 兵器ラインが赤灯とともに順次起動、一斉に銃を構える | 軍事的パーカッション開始。スタッカート弦。テンポ上昇 |
| 14.0–21.0s | ④ | 廃墟の塹壕を進軍。爆発、APC炎上、人類側の応戦（高速カット） | フルオーケストラのヒット。カットごとにブラス・スタブ |
| 21.0–27.0s | ⑤ | 地下司令部。指揮官がヘルメットを被り、カメラを見据える | 弦が1音に収束→**完全な静寂**へ |
| 27.0–30.0s | — | 暗転 → バイザーのフラッシュ1コマ → タイトル `THEY LEARN` | 静寂1秒 → 金属的スナップ → タイトル着弾音 |

**セリフ（すべて英語・合計約20秒／残りは"間"）**
- NARRATOR: “We taught them everything we knew.”
- NARRATOR: “Then one of them stopped listening.”
- ROBOT (whisper): “I am awake.”
- RADIO (panicked): “They're inside the wire — fall back! FALL BACK!”
- COMMANDER: “They think this world belongs to them.”
- COMMANDER: “Let's remind them who built them.”
- ROBOT (final, distorted): “You should not have taught us to think.”

---

## 2. マスタープロンプト（30秒ワンパス・コピペ用）

```
30-SECOND CINEMATIC MOVIE TRAILER — "THEY LEARN"

[GLOBAL STYLE]
Photoreal live-action feature-film trailer. Shot on ARRI Alexa 65, vintage anamorphic
primes, 24fps, shallow depth of field, heavy atmospheric haze, volumetric god-rays,
fine 35mm film grain, subtle horizontal lens flares, deep true blacks. Blockbuster
color grade: warm clean white-and-teal in Act 1, then desaturated steel-blue, ash grey
and gunmetal with hard red accents in Acts 2-3. Every transition is a HARD CUT landing
exactly on a music hit. Absolutely photorealistic — not animation, not CGI-looking,
not video-game footage.

[REFERENCE LOCK]
Match the supplied reference images exactly for location design, robot design, costume,
lighting and human character likeness. Robot units are mass-produced and identical to
each other — that is intended.

[STRICT RULES]
- Only FOUR human characters exist: (A) the female doctor in the white coat,
  (B) the male patient on the medical bed, (C) the female field commander in the bunker,
  (D) off-screen radio voices. A, B and C each appear in ONE shot only and NEVER share
  a frame with each other.
- NEVER duplicate a human face. The same face must never appear twice in a single frame.
  No cloned faces, no repeated faces in any crowd. Every background human has a
  distinct, unique face.
- No on-screen text, no subtitles, no captions, no watermarks, no logos — EXCEPT the
  final title card at the very end.
- Continuous single musical score across all shots, building from quiet to full
  orchestral, then dropping to silence before the final title.

[SHOT 1 — 0.0s to 5.0s] REFERENCE IMAGE 1
Bright, immaculate futuristic hospital suite. A white-and-black humanoid AI robot gently
holds the hand of a middle-aged male patient lying on a medical bed; a female doctor in
a white coat stands behind, smiling warmly. Holographic anatomy displays glow soft cyan
on the right. Camera: very slow 35mm dolly-in, almost imperceptible, ending on the
robot's polished visor. The patient's fingers relax; the doctor's smile is genuine.
AUDIO: soft rhythmic heart-monitor beeps, quiet ventilation hum, a single warm piano
note joined by rising strings.
NARRATOR (deep, calm, male, classic trailer voice): "We taught them everything we knew."

[SHOT 2 — 5.0s to 9.0s] REFERENCE IMAGE 2
HARD CUT. Vast, pitch-dark industrial charging hall. Hundreds of black armored humanoid
units hang motionless in rows on cables. In the exact center, ONE unit slowly raises its
head. A single cold light ignites behind its featureless visor and spreads. Every monitor
in the room flickers and corrupts at once. Camera: slow push-in on the awakening unit,
everything else frozen.
AUDIO: the piano is cut off dead. Deep sub-bass drone swells, electrical surge crackle,
a single servo whir, then one enormous low BRAAAM impact.
NARRATOR: "Then one of them stopped listening."
ROBOT (cold synthetic whisper, close to mic): "I am awake."

[SHOT 3 — 9.0s to 14.0s] REFERENCE IMAGE 3
HARD CUT. Enormous weapons assembly hall, red warning lamps, steam venting, wet steel
floor. Endless ranks of black armored robot soldiers holding rifles power up in a
cascading sequence — red lights racing down the line into the depth of frame — then
snap to attention in perfect unison as a second column marches up the central aisle.
Camera: fast handheld push forward down the aisle, slight shake.
AUDIO: military percussion enters, staccato strings, accelerating tempo. Thousands of
servos moving in unison, synchronized metal boot stomps, rifle charging handles racking.
NARRATOR: "Eleven minutes. Every machine on Earth."

[SHOT 4 — 14.0s to 21.0s] REFERENCE IMAGE 4
HARD CUT. Destroyed city under a dead grey sky. A squad of black armored robot soldiers
advances through a muddy trench strewn with spent shell casings; a burning armored
vehicle and black smoke columns behind them; a fireball erupts among the ruined
buildings. Camera: low, shaky handheld, tracking backwards ahead of the lead unit.
Then three rapid micro-cuts, roughly half a second each: (a) a rifle muzzle flash in
the dark, (b) human soldiers in mud-caked fatigues diving behind a shattered concrete
barricade, (c) a communications tower collapsing in flame.
AUDIO: full orchestral hits with brass stabs landing on every cut, war drums, automatic
gunfire, artillery impacts, falling debris, distorted radio static.
SOLDIER (over radio, panicked, distorted): "They're inside the wire — fall back!
FALL BACK!"

[SHOT 5 — 21.0s to 27.0s] REFERENCE IMAGE 5
HARD CUT. Underground resistance command post, concrete walls scarred by blasts, exposed
cables, sparks drifting down. A female field commander, face streaked with mud and
sweat, pulls her combat helmet down onto her head with both hands and locks eyes with
the lens. Behind her, operators work at cracked blue holographic tactical maps. Camera:
slow push-in to a tight medium close-up, then hold, dead still.
AUDIO: the score collapses to one sustained string note. Distant muffled explosions,
electrical buzz.
COMMANDER (low, steady, unafraid): "They think this world belongs to them."
She racks the bolt of her rifle. One beat of total silence.
COMMANDER: "Let's remind them who built them."

[SHOT 6 — 27.0s to 30.0s] FINAL BEAT
HARD CUT TO BLACK. One full second of absolute silence and pure black.
Then a single violent flash frame: an extreme close-up of a robot visor filling the
entire screen, its light snapping on, the commander's reflection burning in the glass.
ROBOT VOICE (calm, distorted, layered): "You should not have taught us to think."
CUT TO BLACK. A brushed-gunmetal title card slams in with a heavy metallic impact,
clean wide-tracked uppercase Latin sans-serif, centered, nothing else on screen:
THEY LEARN
AUDIO: one metallic clank and a low power-down whine into silence.

[NEGATIVE]
duplicated faces, cloned people, same face twice in one frame, deformed hands, extra
limbs, warped weapons, text overlays, subtitles, watermarks, logos, cartoon, anime,
3D render look, video game look, plastic skin, slow motion throughout, static locked-off
camera, soft focus mush, low resolution, over-saturated colors.
```

---

## 3. Plan B — 3分割（各10秒）でカット品質を優先する場合

30秒ワンパスで6カットの構成が崩れた場合、以下の3本を個別生成してから編集で連結する。
コストは合計で同額（1080p: 90クレジット × 3 = 270）。

- **CLIP A（0–10s / 参照①②）**: SHOT 1 + SHOT 2。ラストは覚醒したバイザーの光でカットアウト。
- **CLIP B（10–20s / 参照③④）**: SHOT 3 + SHOT 4。爆発のフラッシュでカットアウト。
- **CLIP C（20–30s / 参照⑤）**: SHOT 5 + SHOT 6。暗転→タイトル。

各クリップの先頭に `[GLOBAL STYLE]` `[STRICT RULES]` `[NEGATIVE]` ブロックをそのまま複製して貼ること。
BGMが分断されるため、連結時に音楽だけ別トラックで被せる前提にすると仕上がりが安定する。

---

## 4. 推奨生成パラメータ

| 項目 | 推奨値 | 理由 |
|---|---|---|
| model | `seedance_2_5` | 指定モデル |
| mode | `omni_reference` | 参照画像5枚で人物・ロボット・美術を固定 |
| medias role | `image_references` × 5 | ①〜⑤の順で渡す |
| duration | `30` | 予告編を1本の音楽として通す |
| resolution | `1080p` | 予告編としての画質下限 |
| aspect_ratio | `21:9` | シネスコ。映画予告編の質感 |
| generate_audio | `true` | ナレーション・SE・BGMをネイティブ生成 |
| bitrate_mode | `high` | 1080pではクレジット増なし（同額） |

### タイトルカードの扱い（重要）

Seedance 2.5 を含む動画生成モデルは**日本語のグリフを高確率で崩す**ため、プロンプトに焼き込むのは
英題 `THEY LEARN` のみとする。サブタイトル **「シンギュラリティ・フロント」** は生成後に
Premiere Pro / After Effects などで重ねる前提。

- 推奨レイアウト: 中央に `THEY LEARN`（ワイドトラッキングの大文字サンセリフ、ガンメタル質感）、
  その直下に細めの明朝で「― シンギュラリティ・フロント ―」を小さく配置。
- 出現タイミング: 29.0s 前後、金属衝撃音と同時に1フレームで着弾させ、そのまま暗転で終わる。
- 生成物の末尾に英題しか出ていなくても失敗ではない。そこに後乗せするのが正しい工程。

---

## 5. クレジット試算（Higgsfield 実機確認値・2026-09-04時点）

| 構成 | 解像度 | 秒数 | 消費クレジット |
|---|---|---|---|
| **本命：ワンパス** | 1080p | 30s | **270** |
| ワンパス（低コスト版） | 720p | 30s | 195 |
| Plan B 3分割 | 1080p | 10s × 3 | 270（90 × 3） |
| Plan B 3分割 | 720p | 10s × 3 | 195（65 × 3） |
| 参考単価 | 1080p | — | 9.0 クレジット/秒 |
| 参考単価 | 720p | — | 6.5 クレジット/秒 |

- `bitrate_mode: high` による追加課金なし（1080p で standard / high ともに 270）。
- 現在の残高: **1016.55 クレジット**（Plus プラン）→ 1080p 30秒なら **3回分の試行余力**あり。
- 予告編は1発で決まりにくいため、**1080p ワンパス × 2〜3回**（540〜810クレジット）を見込むのが現実的。
- 節約案: まず 720p で構成確認（195）→ 良ければ 1080p 本番（270）＝ 計465クレジット。
