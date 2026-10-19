# Study restyle

A 3D planner for a 276 × 334 cm study with a 2.7 m ceiling.

- The **inspector** at the top of the panel shows room settings (style, paint and wall finish, ceiling light, window/radiator/door, presets, desk arrangements). Click a piece and it swaps to that piece's settings: its version and add-ons, swaps, duplicate, remove. A gizmo slides and turns it.
- Below it, always visible: the list of pieces **in the room**, and a **gallery** of about 80 pieces to drag onto the floor or a wall.

Ctrl/Cmd+Z undoes. The panel keeps a rough cost estimate in Polish złoty.

**Live:** https://aleqsio.github.io/study-restyle/

The whole setup is saved in the page's `#` link, so a copied link reopens the same room.

![Room today, from the photo angle](render_photo_view.png)

## How it's built

Everything is modelled in Blender from simple boxes, cylinders and spheres, to scale.

| File | What it does |
| --- | --- |
| `build_room.py` | The room as it is today: walls, window, door, radiator, wardrobe, desk, chair. Writes `room.blend` and two preview renders. |
| `catalog.py` | Low-poly models for every option (run by `restyle_export.py`). |
| `restyle_export.py` | Adds the options, turns every piece into a template the viewer clones, and exports `viewer/room.json` (a gzipped GLB in a JSON wrapper). |
| `render_og.py` | Renders the social preview card `viewer/og.png`. |
| `viewer/index.html` | The three.js viewer. No build step. |

Rebuild the model (Blender 5.x):

```bash
blender --background --python build_room.py
blender --background room.blend --python restyle_export.py
```

Both scripts write their output next to themselves.

View it locally:

```bash
python3 -m http.server 8765 --directory viewer
```

Pushing to `main` redeploys GitHub Pages from `viewer/`.
