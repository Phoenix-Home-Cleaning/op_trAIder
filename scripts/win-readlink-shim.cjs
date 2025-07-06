/*
 * @fileoverview Windows readlink shim (CommonJS variant)
 * @description
 * This file patches Node's fs.readlink/readlinkSync behaviour on Windows to gracefully
 * handle cases where readlink is called on a directory (EISDIR). When this happens,
 * the shim simply returns the original path instead of throwing, matching *nix
 * semantics.  The logic mirrors the existing ESM implementation but is transpiled
 * to CommonJS so it can be pre-loaded via the `--require` CLI flag – which only
 * supports CJS modules.  This prevents `ERR_REQUIRE_ESM` errors during CI builds
 * with Node 18.
 *
 * IMPORTANT: Do NOT convert this file to ESM.  It **must** stay CommonJS so that
 * the `--require` mechanism works across all supported Node versions.
 */

/* eslint-disable */

// eslint-disable-next-line @typescript-eslint/no-var-requires
const fs = require('fs');

if (process.platform === 'win32') {
  const originalReadlinkSync = fs.readlinkSync.bind(fs);
  const originalReadlink = fs.readlink.bind(fs);

  const normalizeReturn = (p) => (typeof p === 'string' ? p : p.toString());

  fs.readlinkSync = function (pathLike, options) {
    try {
      return originalReadlinkSync(pathLike, options);
    } catch (err) {
      if (err && err.code === 'EISDIR') {
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
      if (err && err.code === 'EISDIR') {
        return callback(null, normalizeReturn(pathLike));
      }
      callback(err, linkString);
    });
  };

  if (fs.promises && fs.promises.readlink) {
    const orig = fs.promises.readlink.bind(fs.promises);
    fs.promises.readlink = async (pathLike, options) => {
      try {
        return await orig(pathLike, options);
      } catch (err) {
        if (err && err.code === 'EISDIR') {
          return normalizeReturn(pathLike);
        }
        throw err;
      }
    };
  }
} 