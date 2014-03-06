import os, stat, errno
try:
        import _find_fuse_parts
except ImportError:
        pass
import fuse

# Specify what Fuse API use: 0.2
fuse.fuse_python_api = (0, 2)


class Calls(object):

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


def myStat(stat):
    stat.st_mode  = 0
    stat.st_ino   = 0
    stat.st_dev   = 0
    stat.st_nlink = 2
    stat.st_uid   = 0
    stat.st_gid   = 0
    stat.st_size  = 0
    stat.st_atime = 0
    stat.st_mtime = 0
    stat.st_ctime = 0
    return stat

class siddharthFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        fuse.Fuse.__init__(self, *args, **kwargs)


        self.fullPath = {'/': Calls(0755 | stat.S_IFDIR)}

    def getattr(self, path):
        if not path in self.fullPath:
            return -errno.ENOENT
	item = self.fullPath[path]
	st = myStat(fuse.Stat())
	st.st_mode  = item.mode
	st.st_size  = len(item.data)
	return st
	'''
	item = self.fullPath[path]
                if not path in self.fullPath:
                        return -errno.ENOENT
                st = myStat(fuse.Stat())
                if path == '/':
                        st.st_mode = stat.S_IFDIR | 0755  #(Remember to try with 644. for now giving 755 permissions to folder) {protection bits}
                        st.st_nlink = 2 #as there are always 2 links in a directory
                        st.st_size  = len(item.data)
                else:
                        st.st_mode = stat.S_IFREG | 0644  #(r--r--r--)
                        st.st_nlink = 1
                        st.st_size = len(item)
                        return st
	'''
    
    def unlink(self, path):
        self.rootRemove(path)
        del self.fullPath[path]

    def mknod(self, path, mode, dev):
        self.fullPath[os.path.dirname(path)].data.add(os.path.basename(path))

    def create(self, path, flags, mode):
        self.fullPath[path] = Calls(mode | stat.S_IFREG)
        self.rootAdd(path)

    def read(self, path, size, offset):
        return self.fullPath[path].read(offset, size)

    def write(self, path, buf, offset):
        return self.fullPath[path].write(offset, buf)

    def mkdir(self, path, mode):
        self.fullPath[path] = Calls(mode | stat.S_IFDIR)
        self.rootAdd(path)


    def rootAdd(self, path):
        parent_path = os.path.dirname(path)
        filename = os.path.basename(path)
        self.fullPath[parent_path].data.add(filename)

    def rmdir(self, path):
        if self.fullPath[path].data:
            return -errno.ENOTEMPTY

        self.rootRemove(path)
        del self.fullPath[path]


    def rootRemove(self, path):
        parent_path = os.path.dirname(path)
        filename = os.path.basename(path)
        self.fullPath[parent_path].data.remove(filename)

    def readdir(self, path, offset):                
        dir_items = self.fullPath[path].data
        for item in dir_items:
            yield fuse.Direntry(item)


if __name__ == '__main__':
	usage = siddharthFS()
        usage.parse(errex=1)
        usage.main()
