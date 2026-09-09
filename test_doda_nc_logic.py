import unittest
import os
import shutil
import tempfile
from doda_nc_logic import copy_item, move_item, delete_item, make_dir

class TestDodaNcLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_make_dir(self):
        new_dir = os.path.join(self.test_dir, "new_folder")
        make_dir(new_dir)
        self.assertTrue(os.path.isdir(new_dir))

    def test_copy_file(self):
        src_file = os.path.join(self.test_dir, "test1.txt")
        with open(src_file, "w") as f:
            f.write("hello")

        dst_file = os.path.join(self.test_dir, "test2.txt")
        copy_item(src_file, dst_file)

        self.assertTrue(os.path.exists(dst_file))
        with open(dst_file, "r") as f:
            self.assertEqual(f.read(), "hello")

    def test_copy_file_to_dir(self):
        src_file = os.path.join(self.test_dir, "test1.txt")
        with open(src_file, "w") as f:
            f.write("hello")

        dst_dir = os.path.join(self.test_dir, "dest_folder")
        os.makedirs(dst_dir)

        copy_item(src_file, dst_dir)

        dst_file = os.path.join(dst_dir, "test1.txt")
        self.assertTrue(os.path.exists(dst_file))

    def test_copy_dir(self):
        src_dir = os.path.join(self.test_dir, "src_folder")
        os.makedirs(src_dir)
        src_file = os.path.join(src_dir, "file.txt")
        with open(src_file, "w") as f:
            f.write("data")

        dst_dir = os.path.join(self.test_dir, "dst_folder")
        copy_item(src_dir, dst_dir)

        self.assertTrue(os.path.exists(os.path.join(dst_dir, "file.txt")))

    def test_copy_dir_to_existing_dir(self):
        src_dir = os.path.join(self.test_dir, "src_folder")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "file.txt"), "w") as f:
            f.write("data")

        dst_dir = os.path.join(self.test_dir, "existing_folder")
        os.makedirs(dst_dir)

        copy_item(src_dir, dst_dir)

        self.assertTrue(os.path.exists(os.path.join(dst_dir, "src_folder", "file.txt")))

    def test_move_item(self):
        src_file = os.path.join(self.test_dir, "move_src.txt")
        with open(src_file, "w") as f:
            f.write("move_me")

        dst_file = os.path.join(self.test_dir, "move_dst.txt")
        move_item(src_file, dst_file)

        self.assertFalse(os.path.exists(src_file))
        self.assertTrue(os.path.exists(dst_file))

    def test_delete_file(self):
        src_file = os.path.join(self.test_dir, "del.txt")
        with open(src_file, "w") as f:
            f.write("del")

        delete_item(src_file)
        self.assertFalse(os.path.exists(src_file))

    def test_delete_dir(self):
        src_dir = os.path.join(self.test_dir, "del_dir")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "file.txt"), "w") as f:
            f.write("del")

        delete_item(src_dir)
        self.assertFalse(os.path.exists(src_dir))

if __name__ == '__main__':
    unittest.main()
