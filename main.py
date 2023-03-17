import os

import decky_plugin
from pathlib import Path
import json
import os
import subprocess
import sys
import shutil
import time


try:
    out_path = str(Path(decky_plugin.DECKY_PLUGIN_DIR) / "backend" / "out" / "vdf")
    if out_path not in sys.path:
        sys.path.append(out_path)
    import vdf

    decky_plugin.logger.info("Successfully loaded vdf library")
except Exception:
    decky_plugin.logger.exception("Could not load vdf library")


class Plugin:
    _id_map = None
    _dump_folder = Path.home() / "Pictures" / "Screenshots"

    async def aggregate_all(self):
        try:
            res = await Plugin.sdsa_classic(self)
            decky_plugin.logger.info(f"Copied {res} files")
            return res
        except Exception:
            decky_plugin.logger.exception("could not")
            return -1

    async def copy_screenshot(self, app_id=0, url=""):
        try:
            decky_plugin.logger.info(f"Copy screenshot: {app_id}, {url}")
            path = Path.home() / ".local/share/Steam/userdata"
            fname = url.split("/")[-1]
            glob_pattern = f"**/760/remote/{app_id}/screenshots/{fname}"
            decky_plugin.logger.info(glob_pattern)
            files = list(path.glob(glob_pattern))
            decky_plugin.logger.info(str(files))
            did = False
            for f in files:
                path = Plugin.make_path(self, app_id, fname)
                os.symlink(f, path)
                most_recent_path = self._dump_folder / "most_recent.jpg"
                if most_recent_path.exists():
                    most_recent_path.unlink()
                os.symlink(f, most_recent_path)
                decky_plugin.logger.info(f"Symlinked {f} to {path}")
                did = True
            return did
        except Exception:
            decky_plugin.logger.exception(f"Copy screenshot: {app_id}, {url}")
            return False

    async def sdsa_classic(self):
        do_copy = False
        if len(sys.argv) > 1 and sys.argv[1] == "copy":
            do_copy = True
        path = Path(decky_plugin.DECKY_USER_HOME) / ".local/share/Steam/userdata"
        files = list(path.glob("**/screenshots/*.jpg"))

        dump_folder = self._dump_folder

        total_copied = 0

        for f in files:
            app_id = int(f.parent.parent.name)
            final_path = Plugin.make_path(self, app_id, f.name)
            if not do_copy:
                if not final_path.exists():
                    os.symlink(f, final_path)
                    total_copied += 1
            else:
                if final_path.is_symlink():
                    final_path.unlink()
                shutil.copy(f, final_path, follow_symlinks=False)
                total_copied += 1

        # clean up
        for f in dump_folder.glob("**/*.jpg"):
            if f.is_symlink() and not f.exists():
                decky_plugin.logger.info(f"Cleaning up broken symlink {f}")
                f.unlink()

        return total_copied

    def make_path(self, app_id, fname):
        final_path = self._dump_folder / str(self._id_map.get(str(app_id), app_id)) / fname
        final_path.parent.mkdir(parents=True, exist_ok=True)
        return final_path

    async def _main(self):
        try:
            decky_plugin.logger.info("Loading appid translations")
            self._id_map = {
                str(i["appid"]): i["name"]
                for i in json.load(open(Path(decky_plugin.DECKY_PLUGIN_DIR) / "assets" / "appidmap.json"))["applist"][
                    "apps"
                ]
            }
            decky_plugin.logger.info("Loading appid translations for nonsteam games")
            for shortcut_file in (Path(decky_plugin.DECKY_USER_HOME) / ".local" / "share" / "Steam" / "userdata").glob(
                "**/shortcuts.vdf"
            ):
                for item in vdf.binary_load(open(shortcut_file, "rb"))["shortcuts"].values():
                    if "appid" not in item:
                        continue
                    decky_plugin.logger.info(str(item))
                    self._id_map[str(item["appid"])] = item["AppName"]

            decky_plugin.logger.info("Initialized")
        except Exception:
            decky_plugin.logger.exception("main")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Calling unload")
        pass
