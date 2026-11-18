"""Create only the installable review ZIP and extract it for final playback."""
from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def package(output=None):
 output=Path(output or ROOT.parent/'output');output.mkdir(parents=True,exist_ok=True)
 dest=output/'Bionic_Commando_HD_v0.12.3.zip';pack=ROOT/'pack'
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in sorted(pack.iterdir()):
   assert p.is_file()and p.suffix in{'.png','.txt'},p
   info=zipfile.ZipInfo(p.name,(2026,11,18,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,p.read_bytes(),compresslevel=9)
 extracted=output/'v0123-extracted';extracted.mkdir(exist_ok=True)
 with zipfile.ZipFile(dest)as z:
  assert z.testzip()is None;z.extractall(extracted)
  assert set(z.namelist())=={p.name for p in pack.iterdir()}
  for n in z.namelist():assert(extracted/n).read_bytes()==(pack/n).read_bytes()
 result={'zip':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'files':len(list(pack.iterdir())),'bytes':dest.stat().st_size}
 (ROOT/'validation/v0123-package.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
 return dest
if __name__=='__main__':package()
