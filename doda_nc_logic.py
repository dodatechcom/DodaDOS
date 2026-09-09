import os
import shutil

def copy_item(src, dst):
    if os.path.isdir(src):
        # if dst is an existing directory, we might want to copy into it, or just use copytree.
        # Actually, if dst exists and is a directory, copytree will fail unless dirs_exist_ok=True (Python 3.8+)
        # To match typical nc behavior: if dst is an existing directory, copy the source folder INTO dst.
        target = dst
        if os.path.isdir(dst):
            target = os.path.join(dst, os.path.basename(src))
            if os.path.exists(target):
                # if target exists, this might be tricky, let's just let shutil raise or handle it.
                if os.path.isdir(target):
                    # We can use dirs_exist_ok=True
                    shutil.copytree(src, target, dirs_exist_ok=True)
                    return
                else:
                    raise FileExistsError(f"{target} exists and is not a directory")
        shutil.copytree(src, target)
    else:
        target = dst
        if os.path.isdir(dst):
            target = os.path.join(dst, os.path.basename(src))
        shutil.copy2(src, target)

def move_item(src, dst):
    # shutil.move handles moving files/directories and moving into existing directories
    shutil.move(src, dst)

def delete_item(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def make_dir(path):
    os.makedirs(path, exist_ok=True)
