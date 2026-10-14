1/ SD-DC now routes pipes and cable trays as MCP/REST services for agents. The trick: search corners, not grid cells. https://sinkers.github.io/devlog/2026/10/13/pipe-router/

2/ A move is a whole straight run, so fabrication rules are part of the move: leave the nozzle straight, ≥2 bend radii between elbows, no 180° turns, no snapped endpoints.

3/ Tested against a real 34-pipe hand-routed chilled-water design. It finds all 34, never longer and never with more elbows. 194.2 m vs 196.4 m.

4/ When a route can't be built, the router says why: blocked_nozzle, enclosed_inlet, no_path…, plus the obstacle and a fix. A failure an agent can act on.

5/ Trays use the same router, plus supports from load tables, AS/NZS 3008 cable sizing, and a FreeCAD → STEP model. MIT: https://github.com/sinkers/sd-dc
