Most auto-routers search a grid and then patch the result to look like pipework. That's backwards. A pipe is straight runs and elbows, and elbows need room.

This week SD-DC got a router that searches corners instead of cells, so the fabrication rules are built into every move: leave the nozzle straight, keep two bend radii between elbows, no 180° turns, never snap an endpoint.

We tested it on a real chilled-water layout of 34 pipes, each routed by hand. It found every one, never with a longer route or more elbows, and came in at 194.2 m against 196.4 m.

The part I care about most: when a route can't be built, it returns the reason, the obstacle and a fix, not a blank. An agent can act on that.

Cable trays now use the same router, with supports from the load table, cables sized to AS/NZS 3008, and a FreeCAD/STEP model out the end.

Write-up with the code: https://sinkers.github.io/devlog/2026/10/13/pipe-router/
