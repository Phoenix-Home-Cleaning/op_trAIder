import fs from 'fs';

if (process.platform === 'win32') {
  const originalReadlinkSync = fs.readlinkSync.bind(fs);
  const originalReadlink = fs.readlink.bind(fs);
  const normalizeReturn = (p) => (typeof p === 'string' ? p : p.toString());

  fs.readlinkSync = function (pathLike, options) {
    try {
      return originalReadlinkSync(pathLike, options);
    } catch (err) {
      if (err?.code === 'EISDIR') {
        return normalizeReturn(pathLike);
      }
      throw err;
    }
  };

  fs.readlink = function (pathLike, options, callback) {
    if (typeof options === 'function') {
      callback = options;
      options = undefined;
    }
    return originalReadlink(pathLike, options, (err, linkString) => {
      if (err?.code === 'EISDIR') {
        return callback(null, normalizeReturn(pathLike));
      }
      callback(err, linkString);
    });
  };

  if (fs.promises?.readlink) {
    const orig = fs.promises.readlink.bind(fs.promises);
    fs.promises.readlink = async (pathLike, options) => {
      try {
        return await orig(pathLike, options);
      } catch (err) {
        if (err?.code === 'EISDIR') {
          return normalizeReturn(pathLike);
        }
        throw err;
      }
    };
  }
} 