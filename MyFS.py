import os
import sys
import stat
import errno
import time
import fuse

fuse.fuse_python_api = (0, 2)

class Item(object):
    def __init__(self, mode):        
        self.mode = mode     
        if stat.S_ISDIR(mode):
            self.data = set()
        else:
            self.data = ''

    def read(self, offset, length):
        return self.data[offset:offset+length]

    def write(self, offset, data):
        length = len(data)
        self.data = self.data[:offset] + data + self.data[offset+length:]
        return length

def zstat(stat):
    stat.st_mode  = 0
    stat.st_ino   = 0
    stat.st_nlink = 2
    stat.st_size  = 0
    return stat

class MyFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        fuse.Fuse.__init__(self, *args, **kwargs)

        
        self._storage = {'/': Item(0755 | stat.S_IFDIR)}

    def getattr(self, path):
        if not path in self._storage:
            return -errno.ENOENT

        item = self._storage[path]
        st = zstat(fuse.Stat())
        st.st_mode  = item.mode
        st.st_size  = len(item.data)
        return st

    def readdir(self, path, offset):                # 'ls' will not work without this function
        dir_items = self._storage[path].data
        for item in dir_items:
            yield fuse.Direntry(item)


    def mkdir(self, path, mode):                    # add a new directory
        self._storage[path] = Item(mode | stat.S_IFDIR)
        self._add_to_parent_dir(path)

    def _add_to_parent_dir(self, path):             # add a path of the directory (to 'ls')
        parent_path = os.path.dirname(path)
        filename = os.path.basename(path)
        self._storage[parent_path].data.add(filename)

    def rmdir(self, path):                          # remove an existing directory
        if self._storage[path].data:
            return -errno.ENOTEMPTY

        self._remove_from_parent_dir(path)
        del self._storage[path]

    def _remove_from_parent_dir(self, path):        # remove the path of the directory (from 'ls') 
        parent_path = os.path.dirname(path)
        filename = os.path.basename(path)
        self._storage[parent_path].data.remove(filename)

    # --- Files --------------------------------------------------------------
    def create(self, path, flags, mode):            # create a new file in my file system when 'cp' is used
        self._storage[path] = Item(mode | stat.S_IFREG)
        self._add_to_parent_dir(path)

    def read(self, path, size, offset):             # read a copied file (when 'cp' is used)
        return self._storage[path].read(offset, size)

    def write(self, path, buf, offset):             # write a copied file into a new file (using 'cp') 
        return self._storage[path].write(offset, buf)

    def unlink(self, path):                         # used to remove a file from a folder (using 'rm')
        self._remove_from_parent_dir(path)
        del self._storage[path]

  
if __name__ == '__main__':  
    fs = MyFS()  
    fs.parse(errex=1)  
    fs.main()
