FuseFS
======

FuseFS
Implemented a FUSE filesystem in Linux using Python.
The filesystem is a pure pass-through filesystem and would accept one directory and expose it under the mountpoint, ensuring that all changes in that mountpoint would be mirrored to the source.
I implemented it without using thin wrappers around the os module.

http://en.wikipedia.org/wiki/Filesystem_in_Userspace
