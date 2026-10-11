# Roomnote — arrange your flat

Download [roomnote-planner.zip](../downloads/roomnote-planner.zip), extract it, and double-click **Roomnote.html** in Chrome, Edge or Firefox on a computer. Everything is included: no account, installation, internet connection or API key is needed. Enable browser hardware acceleration for 3D.

1. The default **whole-flat** template includes L1, kitchen, T1, W1, B1, B2 and the B1 balcony. You can also start with L1 only, B2 only, or an empty room.
2. Click furniture to add it, or drag it from the catalogue onto the plan. Move it by dragging; edit precise dimensions in centimetres on the right.
3. **Openings & more** includes windows, doors, partitions, pillars, a Singhasan, AC and fan. Windows/doors attach to outer or internal walls. Internal walls are selectable items: move or resize them using the inspector; their attached openings follow. Set window height and its elevation above the floor.
4. Use **Room size & walls** to change dimensions or drag wall corners. Changing the room size keeps furniture at its real size; check placement afterward.
5. Switch to **3D view**, orbit with the mouse, or choose a camera. Every angle uses the same layout. Toggle walls off for a clear furniture overview.
6. Click **Save layout** to download your JSON file. Attach it in our chat when ready for a more realistic design render. Include the exported plan or 3D PNG if you want to show a particular view. Use **Open layout** to continue later.

**Save layout is your portable backup.** Browser autosave is convenient but may be unavailable for local files or disappear if browser data is cleared. Save separate files for different rooms/options.

Keyboard: R rotates, D duplicates, Delete removes; arrow keys move 5 cm (Shift for 1 cm); Ctrl/Cmd+Z undoes. Undo also restores a room after changing templates.

The whole-flat trace follows the uploaded plan. Room junctions are approximate, and the balcony has a low outer wall. Use the measured on-site layout to correct walls and openings.

## What is measured and what is provisional

L1 starts from the printed 15′2″ × 16′1″ envelope and the owner's rough arrangement: kitchen access left, main entrance upper-right, TV on the B2 wall, L sofa facing the TV, and two screens around the right-side puja area. L1 has no windows initially. B2 starts at 11′1″ × 14′7″ with its confirmed window behind the bed and no balcony.

Notch size, openings, pillars, ceiling heights and furniture sizes are editable estimates. Correct them using site measurements. This editor does not certify collision-free layouts or walking clearances. Chairs and decorative details are schematic. The live 3D view is a layout preview, not a photorealistic renderer; polished renders are a later step using your saved arrangement.

## Develop and verify

Node 20+:

```sh
npm ci --no-audit --no-fund
npm run build
```

The build bundles Three.js and all styling into `planner.html` and `docs/index.html`; no CDN requests. `docs/index.html` can also be hosted as a static site, but hosting is optional.

Browser smoke test (Python Playwright and Chromium):

```sh
python -m http.server 8765 --bind 127.0.0.1
# In another terminal:
python tests/planner_smoke.py
```

Set `CHROMIUM_PATH` if Chromium is elsewhere. Tests cover furniture editing and drag, wall-attached windows, undo/redo, JSON round-trip and invalid import, camera changes without layout changes, image export, autosave reload and mobile page width. The test switches the browser offline after loading and checks there are no external requests or JavaScript errors.

The managed cloud browser blocks `file://` navigation, so automated tests use local HTTP with subsequent offline interactions; direct double-click launch was not verified in this managed browser. The delivered HTML uses inline CSS/JS and no fetch or module loading, so it is designed for direct local opening in a normal desktop browser.

## Saved layout coordinates

`format: roomnote-layout`, `version: 1`, `units: metres`. Room vertices are clockwise in plan coordinates: x right, y down. Item x/y are centres, w/d/h are width/depth/height, e is elevation, and rotation is clockwise degrees. Doors/windows add a zero-based wall segment and offset from its first vertex. Three.js uses x right, y up, z plan-down; saved camera position/target use those coordinates. Exported geometry and camera allow subsequent renders to preserve the arrangement.
