# RFID on Production Lines: Practical Notes

Field notes from putting RFID readers on conveyor and overhead lines in a wood products plant. Not a vendor comparison, but the decisions that actually decide whether RFID works.

## The one decision that matters most: read range

The first instinct is "more range is better". On a production line it is the opposite.

| | Long-range UHF reader (portal class, up to ~10 m) | Short-range industrial reader (up to ~1 m) |
|---|---|---|
| Good for | dock doors, warehouse gates, inventory counts | process steps on a line |
| On a line | reads tags of neighbouring products, other lines, parts on carts nearby | reads only what is in front of the head |
| Result | **tags assigned to the wrong product** | clean assignment to a process step |

The lesson from the field: a long-range, multi-antenna reader on a line kept reading tags onto the wrong products, and tuning power and antenna angles never made it fully reliable. Short-range heads at each point of interest solved it.

## Think in zones, not items

The goal is not "read exactly one tag". It is "**read everything in this zone, and only this zone**".

- A zone may hold 1 product or 10. What matters is that the zone is physically isolated: a head under a conveyor section, or at height on an overhead hanging line where products are naturally separated.
- One processor unit with several short-range heads (e.g. 4 × ~1 m) covers several zones cheaply.
- Map each zone to a process step in the software: `zone A3 = entered drying`, not `reader 2 antenna 3`.

## Mounting and tags

- Wood is mostly RF-friendly; metal frames, rails and wet surfaces are not. Test with the real product, wet and dry, on the real carrier.
- Tag position must be consistent and must survive the process (paint, heat, sanding). Decide it together with production, not afterwards.
- Leave a margin: design for the worst tag orientation you will actually see.

## Integration

- **MQTT** has been more reliable than raw TCP/IP socket integrations: reconnects, buffering and multiple consumers come for free.
- The reader reports raw reads; your software turns them into events: debounce repeated reads, apply a dwell time, and emit "tag X entered zone Y" once.
- Log raw reads for a while during commissioning. They are the only way to understand cross-reads.

See [docs/event-logic.md](docs/event-logic.md) and [examples/zone_events.py](examples/zone_events.py).

## Buying checklist

- [ ] Read range matches the zone size, not the "max range" in the brochure
- [ ] Number of heads per processor unit, cable lengths
- [ ] Protocol: MQTT / OPC UA / REST available without extra licences?
- [ ] Licence and delivery time for any software connectors (can delay a project by weeks)
- [ ] Industrial rating (IP class, temperature, vibration)
- [ ] A test with your own products before ordering more than one

## License

CC BY 4.0 (docs), MIT (code).
