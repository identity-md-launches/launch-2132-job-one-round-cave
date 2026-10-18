# Gathering 34 image edit

Assigned tool: Replicate image MCP, public `black-forest-labs/flux-kontext-pro`.
Inspected get_models latest_version input schema before creating the prediction.
One image; match_input_image aspect ratio; PNG; prompt_upsampling false;
other values use protocol/model defaults. No private deployment or training.
Prediction `z3w3d703cnrmr0d19k8r8sxc1w` reached succeeded and its PNG was
downloaded using download_prediction_output directly to wall-v14.png.

Input: gathering 33, SHA-256
`4660af2247e6da2479869268e0ee405f870858c282acddb5812af432ffe9c8ab`.

Exact prompt:

> Edit target: the supplied inherited prehistoric cave wall. Preserve its exact square composition, rock texture, cracks, colours, torchlight and framing, and EVERY existing pigment mark without erasing, moving or redrawing any. Add only one small worn red-ochre braided loop on the unused rock at the far right, above the existing faded red knot (around 88% from left, 38% from top). The loop represents four strands of work checked together. Flat thumb-applied earthy pigment, bare rock showing through, Lascaux/Chauvet handmade style. Existing central Pepe frog with wide mouth and heavy-lidded eyes must stay unchanged. Do not add hands or handprints. No text, letters, numbers, captions, signature, watermark, border or new lighting. Keep all ancestral marks identical.

The generated 1024-square draft changed ancestral marks, so it was not retained
as the full wall. Its new loop pigment alone was sampled, flattened to red ochre,
and blended into unused right-side rock of the original 1254-square wall.
The final image replaced the draft at the same required output path; no extra
image was saved. The helper uses the existing ordinary-file JPEG encoder for
the 512-square preview. Its one-time application must not be repeated.

Worker-selected choices: subdued loop motif, model, patch location and pigment
compositing to enforce ancestral preservation. All pixels outside the 95 × 95
patch match the input. Review found no new hands, text or forbidden marks;
Pepe and inherited rock/framing remain intact. The loop is small in the preview.
No unmet visual requirement was identified. Details: image-preservation-34.json.
