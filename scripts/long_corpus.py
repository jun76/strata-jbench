#!/usr/bin/env python3
"""The long document of Tiers 4b–4d: five Japanese works (Aozora Bunko) and five English ones (Project Gutenberg),
cleaned and laid out chunk by chunk in turn (ja, en, ja, en, …), so that every prefix of it holds both languages.

    python3 -I scripts/long_corpus.py

Reads the downloads in work/corpus/raw/ (Git-ignored; SOURCES says where each came from) and writes
prompts/long-corpus.txt and prompts/long-sources.json (both tracked). scripts/build_fixtures.py then cuts the
fixtures long-32K … long-1M out of it and places the facts the questions ask about.

All ten authors died before 1956, so the works are out of copyright in Japan and the United States. Aozora's ruby,
input notes and header are removed and its colophon (底本・入力・校正) kept in long-sources.json; Project Gutenberg's
header, footer and licence (its name is a trademark) are removed, leaving the public-domain text alone.
"""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'work' / 'corpus' / 'raw'
OUT = ROOT / 'prompts'

# (language, title, author, died, file in RAW, where it came from)
SOURCES = [
    ('ja', '吾輩は猫である', '夏目漱石', 1916, '789_ruby_5639.zip', 'https://www.aozora.gr.jp/cards/000148/card789.html'),
    ('ja', '破戒', '島崎藤村', 1943, '1502_ruby_24534.zip', 'https://www.aozora.gr.jp/cards/000158/card1502.html'),
    ('ja', '或る女（前編）', '有島武郎', 1923, '201_ruby_2682.zip', 'https://www.aozora.gr.jp/cards/000025/card201.html'),
    ('ja', '或る女（後編）', '有島武郎', 1923, '202_ruby_20065.zip', 'https://www.aozora.gr.jp/cards/000025/card202.html'),
    ('ja', '人間失格', '太宰治', 1948, '301_ruby_5915.zip', 'https://www.aozora.gr.jp/cards/000035/card301.html'),
    ('ja', '銀河鉄道の夜', '宮沢賢治', 1933, '43737_ruby_19028.zip', 'https://www.aozora.gr.jp/cards/000081/card43737.html'),
    ('en', 'Moby-Dick; or, The Whale', 'Herman Melville', 1891, 'pg2701.txt', 'https://www.gutenberg.org/ebooks/2701'),
    ('en', 'Pride and Prejudice', 'Jane Austen', 1817, 'pg1342.txt', 'https://www.gutenberg.org/ebooks/1342'),
    ('en', 'A Tale of Two Cities', 'Charles Dickens', 1870, 'pg98.txt', 'https://www.gutenberg.org/ebooks/98'),
    ('en', 'Frankenstein; or, The Modern Prometheus', 'Mary Wollstonecraft Shelley', 1851, 'pg84.txt',
     'https://www.gutenberg.org/ebooks/84'),
    ('en', 'The Adventures of Sherlock Holmes', 'Arthur Conan Doyle', 1930, 'pg1661.txt', 'https://www.gutenberg.org/ebooks/1661'),
]
# a chunk is about 2,000 tokens in either language (Japanese ~1.4 characters a token, English ~4.2)
CHUNK_CHARS = {'ja': 3000, 'en': 9000}


def aozora(path):
    """The body of an Aozora ruby text, and its colophon."""
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith('.txt'))
        text = z.read(name).decode('cp932').replace('\r\n', '\n')
    seps = [m.start() for m in re.finditer(r'^-{20,}$', text, re.M)]
    body = text[text.index('\n', seps[1]) + 1:] if len(seps) >= 2 else text.split('\n', 2)[2]
    body, _, colophon = body.partition('\n底本：')
    body = re.sub(r'※?［＃[^］]*］', '', body)        # input notes (headings, emphasis, external characters)
    body = re.sub(r'《[^》]*》', '', body).replace('｜', '')   # ruby
    paras = [ln.strip('　 ') for ln in body.split('\n')]
    return [p for p in paras if p], ('底本：' + colophon).strip()


def gutenberg(path):
    """The text between Project Gutenberg's START and END lines, in paragraphs (wrapped lines joined)."""
    text = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    start = re.search(r'^\*\*\* START OF TH(E|IS) PROJECT GUTENBERG EBOOK.*$', text, re.M)
    end = re.search(r'^\*\*\* END OF TH(E|IS) PROJECT GUTENBERG EBOOK.*$', text, re.M)
    body = text[start.end():end.start()]
    paras = [' '.join(p.split()) for p in re.split(r'\n\s*\n', body)]
    paras = [p for p in paras if p and not p.lower().startswith(('produced by', 'transcriber', '[illustration'))
             and 'gutenberg' not in p.lower()]    # notes on the e-text, not the work
    return paras


def chunks(lang, paras, head):
    out, cur, n = [], [head], len(head)
    for p in paras:
        cur.append(p)
        n += len(p)
        if n >= CHUNK_CHARS[lang]:
            out.append(cur)
            cur, n = [], 0
    if cur:
        out.append(cur)
    return out


def main():
    streams = {'ja': [], 'en': []}
    sources = []
    for lang, title, author, died, fname, url in SOURCES:
        path = RAW / fname
        if lang == 'ja':
            paras, colophon = aozora(path)
            head = f'『{title}』{author}'
        else:
            paras, colophon = gutenberg(path), None
            head = f'{title} — {author}'
        streams[lang] += chunks(lang, paras, head)
        sources.append({'lang': lang, 'title': title, 'author': author, 'died': died, 'url': url, 'file': fname,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'paragraphs': len(paras),
                        'chars': sum(map(len, paras)), **({'colophon': colophon} if colophon else {})})
    # ja, en, ja, en, … as far as both last (about 1.2M tokens: more than the longest fixture); the rest is not used
    order = [c for pair in zip(streams['ja'], streams['en']) for c in pair]
    text = '\n\n'.join('\n'.join(c) for c in order) + '\n'
    OUT.mkdir(exist_ok=True)
    (OUT / 'long-corpus.txt').write_text(text, encoding='utf-8')
    (OUT / 'long-sources.json').write_text(json.dumps({
        'note': 'The long document of Tiers 4b-4d (prompts/long-corpus.txt), built by scripts/long_corpus.py. '
                'Aozora Bunko texts with ruby and input notes removed (colophons kept here); Project Gutenberg texts '
                'without its header, footer and licence. All authors died before 1956.',
        'chunks': {'ja': len(order) // 2, 'en': len(order) // 2},
        'sha256': hashlib.sha256(text.encode()).hexdigest(), 'chars': len(text), 'works': sources},
        ensure_ascii=False, indent=2) + '\n')
    print(f'long-corpus.txt: {len(text):,} characters, {len(order) // 2} ja + {len(order) // 2} en chunks')
    for s in sources:
        print(f'  {s["lang"]} {s["title"]}: {s["chars"]:,} characters')


if __name__ == '__main__':
    main()
