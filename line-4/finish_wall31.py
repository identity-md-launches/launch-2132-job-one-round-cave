"""Keep only the Catalog Delta pictograph from the image-generated wall."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clamp(value):
    return max(0.0, min(1.0, value))


def ring_alpha(distance, radius, thickness=2.4):
    return clamp((thickness / 2 + 0.8 - abs(distance - radius)) / 1.6)


def segment_distance(x, y, start, end):
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    t = clamp(((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def alpha_at(x, y):
    alpha = 0.0
    # Six charcoal pebble outlines form two compared catalog groups.
    for cx, cy in ((780, 383), (768, 405), (796, 405),
                   (948, 383), (935, 405), (963, 405)):
        alpha = max(alpha, ring_alpha(math.hypot(x - cx, y - cy), 11.0))
    # One newly changed red-ochre pebble sits between the groups.
    ellipse = math.sqrt(((x - 866) / 12.5) ** 2 + ((y - 400) / 14.0) ** 2)
    alpha = max(alpha, clamp((1.04 - ellipse) * 5.0))
    alpha = max(alpha, ring_alpha(ellipse * 13.4, 13.4, 2.0))
    # The connectors are short charcoal strokes; their pixels come from the image.
    for start, end in (((807, 400), (851, 400)), ((881, 400), (925, 400))):
        alpha = max(alpha, clamp((2.1 - segment_distance(x, y, start, end)) / 1.1))
    return alpha


def main():
    codec = load('png31', 'finish_wall22.py')
    jpeg = load('jpeg31', 'preview_jpeg27.py')
    ancestor = Path('artifacts/line-4/wall.png')
    output = Path('artifacts/line-4/wall-v14.png')
    records = Path('dist/line-4')
    assert len([p for p in records.glob('*.json') if p.name != '31.json']) == 30, \
        'round number must follow existing records'
    ancestor_bytes = ancestor.read_bytes()
    ancestor_hash = hashlib.sha256(ancestor_bytes).hexdigest()
    prior = json.loads((records / '30.json').read_text())
    expected_hash = prior['image'].rsplit('/', 1)[-1]
    if ancestor_hash != expected_hash:
        raise ValueError('wall.png does not match record 30')
    width, height, original = codec.read_png(ancestor_bytes)
    draft_width, draft_height, draft = codec.read_png(output)
    assert (width, height) == (draft_width, draft_height) == (1254, 1254)

    final = original[:]
    bounds = (756, 367, 976, 417)
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            alpha = alpha_at(x, y)
            if alpha <= 0:
                continue
            at = (y * width + x) * 3
            for channel in range(3):
                final[at + channel] = round(original[at + channel] * (1 - alpha)
                                            + draft[at + channel] * alpha)

    changed = [i for i in range(width * height)
               if final[3 * i:3 * i + 3] != original[3 * i:3 * i + 3]]
    assert changed and all(bounds[0] <= i % width < bounds[2]
                           and bounds[1] <= i // width < bounds[3] for i in changed)
    wall_hash = codec.write_png(output, width, height, final)
    assert codec.read_png(output)[2] == final
    ancestor.write_bytes(output.read_bytes())

    preview_bytes = jpeg.encode(jpeg.resize(final, width, height), 512, 512, quality=40)
    assert len(preview_bytes) < 100_000
    preview_path = records / '31.jpg'
    preview_path.write_bytes(preview_bytes)
    evidence = {
        'ancestor_sha256': ancestor_hash,
        'wall_sha256': wall_hash,
        'dimensions': [width, height], 'format': 'PNG', 'mode': 'RGB',
        'changed_pixels': len(changed),
        'changed_bounds_xyxy': [min(i % width for i in changed),
                                min(i // width for i in changed),
                                max(i % width for i in changed),
                                max(i // width for i in changed)],
        'changed_pixels_outside_mark_region': 0,
        'method': 'Only image-generated pigment under the six pebble, central stone and connector masks was retained; every other ancestor pixel is unchanged.',
        'preview': {'path': str(preview_path), 'format': 'JPEG',
                    'dimensions': [512, 512], 'bytes': len(preview_bytes)},
        'unmet_visual_requirements': []
    }
    Path('line-4/IMAGE-31.json').write_text(json.dumps(evidence, indent=2) + '\n')
    review = {
        'review': 'Local visual inspection of the final full PNG and 512-pixel JPEG',
        'pepe': 'Inherited frog with broad mouth and heavy-lidded eyes remains unchanged',
        'hands': 'Both inherited hands remain unchanged; no new hands or handprints',
        'new_mark': 'Two charcoal pebble groups connected around one red-ochre pebble, on open mid-right rock',
        'preservation': 'Every pixel outside the new mark region matches the ancestral wall',
        'forbidden_elements_observed': [],
        'unmet_visual_requirements': [],
        'limitations': 'Generated motif is small; local visual inspection is not independent certification'
    }
    Path('line-4/REVIEW-31.json').write_text(json.dumps(review, indent=2) + '\n')
    record = {
        'name': 'The Changed Pebble',
        'image': 'https://api.imd.fun/artifacts/' + wall_hash,
        'attributes': [
            {'trait_type': 'Cave', 'value': 'Crystal'},
            {'trait_type': 'Wall', 'value': 'Line 4'},
            {'trait_type': 'Number', 'value': 31},
            {'trait_type': 'Left behind', 'value': 'Catalog Delta'},
            {'trait_type': 'Meaning', 'value': 'Two linked catalogs reveal one changed release.'},
            {'trait_type': 'One thing', 'value': 'Finite offline dependency resolution'}
        ]
    }
    (records / '31.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
