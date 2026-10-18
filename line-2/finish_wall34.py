"""Retain only image-tool pigment on unused rock; preserve all ancestor marks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

spec = importlib.util.spec_from_file_location('png34', 'gathering/finish_wall.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)
OLD = Path('artifacts/line-2/wall-v13.png')
NEW = Path('artifacts/line-2/wall-v14.png')
RECT = (65, 375, 100, 150)


def main():
    ancestor = hashlib.sha256(OLD.read_bytes()).hexdigest()
    assert ancestor == '39f11eb039d51162de4a57b96f14cb80d4eea152719b6ca18c585a152cbd3fd2'
    generated = hashlib.sha256(NEW.read_bytes()).hexdigest()
    assert generated == 'f5efdf38acdf2fa27b911571bd6e67bb917b285717baae327168b5f15e629625', 'expected original generated draft; do not run twice'
    width, height, original = png.read_png(OLD)
    dw, dh, draft = png.read_png(NEW)
    assert (width, height) == (dw, dh) == (1254, 1254)
    final = original[:]
    dx, dy, pw, ph = RECT
    for y in range(dy, dy+ph):
        for x in range(dx, dx+pw):
            at = (y*width+x)*3
            r, g, b = draft[at:at+3]
            ochre = r > 65 and r > 1.6*g and r > 2.1*b
            # Inside the generated seed's silhouette retain its two charcoal bands.
            interior = ((x-115)/31)**2 + ((y-453)/64)**2 < 1
            charcoal = interior and r < 90 and g < 68 and b < 50
            chalk = ((x-115)/12)**2 + ((y-458)/13)**2 < 1 and r > 140 and g > 110
            if ochre or charcoal or chalk:
                fade = max(0, min(1, (x-dx)/6, (y-dy)/6,
                                  (dx+pw-1-x)/6, (dy+ph-1-y)/6))
                alpha = .88*fade
                for c in range(3):
                    final[at+c] = round(original[at+c]*(1-alpha)+draft[at+c]*alpha)
    changed = outside = 0
    for i in range(width*height):
        if final[3*i:3*i+3] != original[3*i:3*i+3]:
            changed += 1
            x, y = i % width, i // width
            outside += not (dx <= x < dx+pw and dy <= y < dy+ph)
    assert changed > 1000 and outside == 0
    digest = png.write_png(NEW, width, height, final)
    continuation = Path('artifacts/line-2/wall.png')
    if continuation.is_symlink():
        continuation.unlink()
    continuation.symlink_to('wall-v14.png')
    rgba = bytearray()
    for y in range(512):
        ya, yb = y*height//512, (y+1)*height//512
        for x in range(512):
            xa, xb = x*width//512, (x+1)*width//512
            count = (yb-ya)*(xb-xa)
            for c in range(3):
                rgba.append(round(sum(final[(sy*width+sx)*3+c]
                                      for sy in range(ya,yb) for sx in range(xa,xb))/count))
            rgba.append(255)
    js = """
const fs=require('fs');
const encode=require('./line-3/tools/corpus-change-receipt/vendor/jpeg-js/lib/encoder.js');
const result=encode({data:fs.readFileSync(0),width:512,height:512},78);
if(result.data.length>100000)throw Error('JPEG too large');
fs.writeFileSync('dist/line-2/34.jpg',result.data);
"""
    subprocess.run(['node','-e',js],input=rgba,check=True)
    report = {'round':34, 'ancestorSha256':ancestor, 'generatedDraftSha256':generated,
              'wallSha256':digest, 'dimensions':[width,height], 'format':'PNG', 'channels':'RGB',
              'newMarkRectangle':list(RECT), 'changedPixels':changed,
              'changedPixelsOutsideRectangle':outside,
              'method':'Built-in image edit; only generated seed-pod pigment composited onto unused left rock. All other ancestor pixels preserved exactly.',
              'visualReview':'Pending final inspection', 'unmetVisualRequirements':[], 'images':[]}
    for path, kind, size in ((NEW,'PNG',[1254,1254]),(continuation,'PNG',[1254,1254]),
                             (Path('dist/line-2/34.jpg'),'JPEG',[512,512])):
        data = path.read_bytes()
        report['images'].append({'path':str(path), 'format':kind, 'dimensions':size,
                                 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
    Path('line-2/REVIEW-34.json').write_text(json.dumps(report,indent=2)+'\n')
    traits = [('Cave','Crystal'),('Wall','Line 2'),('Number',34),('Left behind','Storage Fields'),
              ('Meaning','A banded ochre seed reveals smaller parts within a proven whole.'),
              ('One thing','Verify Ethereum account and storage proofs against trusted state roots')]
    record = {'name':'Inside the Seed','image':'https://api.imd.fun/artifacts/'+digest,
              'attributes':[{'trait_type':key,'value':value} for key,value in traits]}
    Path('dist/line-2/34.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
