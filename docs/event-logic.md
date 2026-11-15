# From raw reads to zone events

A reader in a zone reports the same tag many times per second. Production software needs one event: "product X entered step Y at time T".

## States per (tag, zone)

```
 absent ──first read──► present ──no read for exit_timeout──► absent
             │                        │
         emit ENTER               emit EXIT (optional)
```

## Parameters

| Parameter | Typical | Purpose |
|---|---|---|
| `min_reads` | 2–3 | ignore single stray reads (cross-reads) |
| `window` | 1–2 s | time window in which `min_reads` must occur |
| `exit_timeout` | 3–10 s | how long without reads before the tag is considered gone |
| `reentry_block` | 30–300 s | do not emit ENTER again if the tag bounces at the zone edge |

## Rules that prevent most errors

- **A tag can be in only one zone of the same line at a time.** If it shows up in the next zone, close the previous one.
- **Order matters.** If a tag appears in step 5 without step 4, flag it instead of silently accepting it.
- **Keep raw reads separately** from events, at least during commissioning, with reader, antenna, RSSI and timestamp.
- **Use RSSI as a tie-breaker** when the same tag is seen by two neighbouring heads at once: the stronger signal wins.
