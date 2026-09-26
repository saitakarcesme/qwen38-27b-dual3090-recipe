"""Build a non-repeated source corpus from ordered, local source directories."""
import argparse
import hashlib
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('roots',nargs='+',type=Path)
    p.add_argument('--out',type=Path,default=Path('code-corpus.txt'))
    a=p.parse_args();seen=set();parts=[];manifest=[]
    for index,root in enumerate(a.roots):
        if not root.is_dir():p.error(f'Missing source directory: {root}')
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.suffix not in ('.py','.cu','.cuh','.h','.cpp') or path.stat().st_size>500000:continue
            data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
            if digest in seen:continue
            seen.add(digest);relative=path.relative_to(root).as_posix()
            parts.append('\n### FILE '+relative+'\n'+data.decode('utf8',errors='replace')+'\n')
            manifest.append(dict(root_index=index,path=relative,sha256=digest,bytes=len(data)))
    if not parts:p.error('No eligible source files found')
    a.out.write_text(''.join(parts),encoding='utf8')
    a.out.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(f'{len(manifest)} unique source files; {a.out.stat().st_size} bytes')

if __name__=='__main__':main()
