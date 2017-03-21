"""Utility methods."""
import os
import os.path
import errno


def map_files(files):
    """Maps a list of files to basename -> path."""
    output = {}
    for f in files:  # pylint: disable=invalid-name
        basename = os.path.splitext(os.path.basename(f))[0]
        output[basename] = f
    return output


def mkpath(path):
    """Alias for mkdir -p."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
