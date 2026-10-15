"""Dependency-free GitHub Pages build. Never deploys or changes source pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,shutil,re,json

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
OUT=ROOT/'.build/pages'
ORIGIN='https://yaelglo.github.io'
FILES=['index.html','merge-alchemy.html','css/homepage.css','css/portfolio.css','css/case-study.css','assets/favicon.svg','assets/manrope.ttf','assets/manrope-license.txt','assets/hero-waves.webp','assets/merge-alchemy-800.webp','assets/merge-alchemy-1600.webp']
parser=argparse.ArgumentParser()
FILES.extend(str(p.relative_to(SITE)).replace('\\','/') for p in sorted((SITE/'assets/history').glob('*.webp')))
parser.add_argument('--require-resume',action='store_true',help='Block publication builds until the real resume PDF is supplied.')
args=parser.parse_args()
resume=SITE/'assets/resume.pdf'
if args.require_resume and not resume.is_file():raise SystemExit('Resume required: place your real PDF at site/assets/resume.pdf. No placeholder will be generated.')
if resume.exists():
    if resume.read_bytes()[:5]!=b'%PDF-':raise SystemExit('site/assets/resume.pdf is not a PDF file.')
    FILES.append('assets/resume.pdf')
if OUT.is_symlink() or not OUT.resolve().is_relative_to(ROOT.resolve()):raise SystemExit('Unsafe build output path.')
# Only generated output is replaced; source and historical files remain untouched.
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir(parents=True)
for name in FILES:
    src=SITE/name
    if not src.is_file():raise SystemExit('Missing production source: '+name)
    dest=OUT/name;dest.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix!='.html':shutil.copy2(src,dest);continue
    text=src.read_text(encoding='utf-8')
    if name=='index.html' and resume.exists():
        text=re.sub(r'<span[^>]*class="resume-link unavailable"[^>]*>Resume</span>','<a class="resume-link" href="assets/resume.pdf" target="_blank" rel="noopener" aria-label="Resume PDF (opens in a new tab)">Resume</a>',text)
    canonical=ORIGIN+('/' if name=='index.html' else '/'+name)
    metadata=f'<link rel="canonical" href="{canonical}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{ORIGIN}/assets/merge-alchemy-1600.webp"><meta property="og:image:width" content="1600"><meta property="og:image:height" content="900"><meta property="og:image:alt" content="Authentic Merge Alchemy gameplay"><meta name="twitter:image" content="{ORIGIN}/assets/merge-alchemy-1600.webp"><meta name="twitter:image:alt" content="Authentic Merge Alchemy gameplay">'
    text=text.replace('name="twitter:card" content="summary"','name="twitter:card" content="summary_large_image"')
    text=re.sub(r'<!-- Social image and canonical URLs.*?-->','',text)
    text=text.replace('</head>',metadata+'</head>')
    dest.write_text(text,encoding='utf-8')
(OUT/'.nojekyll').touch()
class Page(HTMLParser):
    def __init__(self,text):super().__init__();self.ids=set();self.refs=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        for k in ('href','src'):
            if a.get(k):self.refs.append(a[k])
        if a.get('srcset'):self.refs.extend(x.strip().split()[0] for x in a['srcset'].split(','))
def exact(path):
    current=OUT
    for part in path.relative_to(OUT).parts:
        if not current.is_dir() or part not in [p.name for p in current.iterdir()]:return False
        current=current/part
    return current.is_file()
for name in ('index.html','merge-alchemy.html'):
    page=Page((OUT/name).read_text(encoding='utf-8'))
    for ref in page.refs:
        url=urlsplit(ref)
        if url.scheme:continue
        target=OUT/unquote(url.path) if url.path else OUT/name
        assert exact(target),f'Missing/case mismatch: {name}: {ref}'
        if url.fragment and target.suffix=='.html':assert url.fragment in Page(target.read_text(encoding='utf-8')).ids,f'Broken anchor: {ref}'
for name in ('homepage.css','portfolio.css','case-study.css'):
    for ref in re.findall(r'url\(["\x27]?([^\)"\x27]+)',(OUT/'css'/name).read_text(encoding='utf-8')):
        if ref.startswith('data:'):continue
        assert exact((OUT/'css'/unquote(ref)).resolve()),f'Missing CSS asset: {ref}'
print(json.dumps({'build':'passed','output':str(OUT),'root_url':ORIGIN+'/','resume_included':resume.exists(),'public_files':len(FILES)+1,'internal_links_assets_case_checks':'passed'}))
