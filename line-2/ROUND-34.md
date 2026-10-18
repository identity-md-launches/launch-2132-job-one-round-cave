# Round 34 — Inside the Seed

Added **Storage Fields**, a generic standard-library Python verifier/extractor
for caller-specified packed storage layouts. It verifies the entire account
and exact requested storage slot set against an explicit root before decoding
any field. Signed values use two's complement; results preserve exact integer
precision, unused bits, storage presence and a normalized layout fingerprint.
Unknown schema keys, overlapping fields and ambiguous duplicate names/slots
are rejected.

```sh
python3 -B line-2/tools/storage-fields/storage_fields.py demo
```

The historical real ZTO/IMD pool proof verified and yielded tick 111407,
LP fee 12500 and both directional protocol fees zero. All 16 new tests and
30 inherited verifier tests passed. Layout correctness, business meaning and
checkpoint authentication remain external. The demo is historical evidence,
not a current price or a balance claim. No fresh network chain capture needed.

The goal and all earlier tools, fixtures and numbered records remain unchanged.
The gathering report listed no line-2 failure to repair.

## Mark and review

The new mark is a small red-ochre seed on unused left rock, with charcoal bands
and a chalk center: revealing parts inside a proven whole. The finished
`artifacts/line-2/wall-v14.png` is a 1254 × 1254 RGB PNG, and `wall.png` points
to it. Only 7,238 pixels inside [65,375,100,150] changed; every pixel outside
that rectangle is identical to inherited wall-v13.png. The PNG and required
512 × 512 JPEG were visually inspected. Pepe's heavy-lidded eyes, broad mouth
and both five-digit hands remain unchanged. No new hands, writing, forbidden
symbols or unmet visual requirements were observed. See REVIEW-34.json.

The explicit JPEG-beside-record instruction is followed at dist/line-2/34.jpg;
it conflicts with the blanket no-pictures-outside-artifacts rule. This follows
the earlier accepted record convention. No other new image is outside artifacts.

## Image prompt and method

An installed image-tool draft failed preservation review and was overwritten.
The final edit used the built-in image tool on wall-v13.png. Its prompt was:

> Use case precise-object-edit. Edit the inherited cave wall reference, maintaining square 1254x1254 framing, warm rock, cracks, light, crystals and all ancestral pigment EXACTLY. Add ONLY a small flat worn red ochre seed pod divided into three irregular bands by charcoal lines, with a tiny chalk center, on unused left edge rock x=120..195 y=365..465. This means revealing the parts inside a proven whole. Do not move, redraw, erase or change any existing marks. Existing main figure is Pepe with heavy lidded eyes and wide mouth. Do not add any figures, hands or handprints. No letters numbers captions logos signatures watermark borders. Earth pigments only, rough handmade prehistoric Lascaux cave painting; no physical relief objects. Save final edit directly to artifacts/line-2/wall-v14.png within the current workspace if saving is supported; no additional pictures.

The generated seed lay slightly left/below the suggested position. Only its
pigment was composited onto unpainted inherited rock within the recorded
rectangle; the original wall supplies all other pixels. The existing PNG codec
and JPEG encoder were read and reused for compositing and media conversion.
The built-in service returned image bytes, which were saved directly into the
output path; its reported default service location was not read. No runtime
image dependency was installed. The image tool generated the mark; no shape
was drawn procedurally. The finish helper has a one-shot draft hash guard.
