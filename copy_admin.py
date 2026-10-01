import shutil
from pathlib import Path

src = Path('/root/nexmedia/staticfiles/admin')
dst = Path('/root/nexmedia/static/admin')

if src.exists():
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print("Admin static files successfully copied to static/admin!")
else:
    print("Source staticfiles/admin does not exist!")
