[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/fuziolee/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/fuziolee/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# One day of world news in one picture — 21 November 2026

An entry for [make.fun's news-image-20261121 bounty](https://make.fun/bounty/news-image-20261121):
sum up Saturday 21 November 2026's world news in a single image.

`main.py` draws a dense 1024×1024 newspaper front page with Pillow:
a masthead dated 21 November 2026, a UTC timeline of the day,
4 hero stories, 12 more stories in brief, a world map of where it
happened, 34 one-line stories, and a red date check. 50 sourced
stories across 7 regions in all — from Russia's strikes on Ukraine
and the ICJ's Rohingya genocide ruling to the AI stock rout, the
Shenzhen summit, and GTA VI's $3.8bn first day.

Run it with:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `out/entry.png` (1024×1024, under 1 MiB, deterministic —
two runs produce identical bytes). If Pillow is unavailable it falls
back to the pre-rendered `entry.png` shipped beside it.
No network is used.
