import os

from click import get_app_dir
import decky_plugin
from pathlib import Path
import json
import os
import subprocess
import sys
import shutil
import time
import asyncio


class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    _id_map = {}
    _id_map_frontend = {}
    _trunc_id_map = {}
    _dump_folder = Path.home() / "Pictures" / "Screenshots"
    _rescuer_task = None
    _current_app_name = "Unknown"
    _rescued = False

    async def screenshot_rescuer(self):
        png_path = "/tmp/gamescope.raw_encoded.png"
        raw_path = "/tmp/gamescope.raw"
        decky_plugin.logger.info("Rescuer started")
        while True:
            try:
                if os.path.exists(png_path):
                    dt = time.time() - os.path.getmtime(png_path)
                    if dt > 2:
                        path = (
                            Plugin._dump_folder
                            / Plugin._current_app_name.replace(":", " ")
                            / (str(int(time.time())) + ".png")
                        )
                        path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(png_path, path)
                        shutil.copy(png_path, self._dump_folder / "most_recent.jpg")
                        os.unlink(png_path)
                        os.unlink(raw_path)
                        decky_plugin.logger.info(
                            f"Rescued screenshot for {Plugin._current_app_name}"
                        )
                        Plugin._rescued = True
            except Exception:
                decky_plugin.logger.exception("watchdog")
            await asyncio.sleep(0.5)

    async def aggregate_all(self, allapps):
        self._id_map_frontend = {a[0]: a[1] for a in allapps}
        try:
            res = await Plugin.sdsa_classic(self)
            decky_plugin.logger.info(f"Copied {res} files")
            return res
        except Exception:
            decky_plugin.logger.exception("could not")
            return -1

    async def was_rescued(self):
        if Plugin._rescued:
            Plugin._rescued = False
            return True
        return False

    async def set_current_app_name(self, app_name):
        decky_plugin.logger.info("setting app name to " + app_name)
        Plugin._current_app_name = app_name

    async def set_id_map_fronend(self, allapps):
        self._id_map_frontend = {a[0]: a[1] for a in allapps}
        decky_plugin.logger.info("Set frontend id map")

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
                os.link(f, path)
                most_recent_path = self._dump_folder / "most_recent.jpg"
                if most_recent_path.exists():
                    most_recent_path.unlink()
                os.link(f, most_recent_path)
                decky_plugin.logger.info(f"Copied {f} to {path}")
                did = True
            return did
        except Exception:
            decky_plugin.logger.exception(f"Copy screenshot: {app_id}, {url}")
            return False

    async def sdsa_classic(self):
        id_map = self._id_map
        path = Path.home() / ".local/share/Steam/userdata"
        files = list(path.glob("**/screenshots/*.jpg"))

        dump_folder = self._dump_folder

        total_copied = 0

        for f in files:
            app_id = int(f.parent.parent.name)
            final_path = Plugin.make_path(self, app_id, f.name)
            if not final_path.exists():
                os.link(f, final_path)
                total_copied += 1

        # clean up
        for f in dump_folder.glob("**/*.jpg"):
            if f.is_symlink() and not f.exists():
                decky_plugin.logger.info(f"Cleaning up broken symlink {f}")
                f.unlink()

        return total_copied

    def get_app_name(self, app_id):
        if app_id in self._id_map_frontend:
            return self._id_map_frontend[app_id]
        if app_id in self._id_map:
            return self._id_map[app_id]
        # At this point we probably have a non-steam app, where the ID in the screenshot is sent back wrong
        if app_id in self._trunc_id_map:
            return self._trunc_id_map[app_id]
        for _id, name in self._id_map_frontend.items():
            if bin(_id).endswith(bin(app_id)[2:]):
                self._trunc_id_map[app_id] = name
                decky_plugin.logger.info(f"Found name of {app_id} to be {name}")
                return name

    def make_path(self, app_id, fname):
        app_name = Plugin.get_app_name(self, app_id) or str(app_id)
        final_path = self._dump_folder / app_name.replace(":", " ") / fname
        final_path.parent.mkdir(parents=True, exist_ok=True)
        return final_path

    async def _main(self):
        try:
            loop = asyncio.get_event_loop()
            Plugin._rescuer_task = loop.create_task(Plugin.screenshot_rescuer(self))
            decky_plugin.logger.info("Loading appid translations")
            self._id_map = {
                i["appid"]: i["name"]
                for i in json.load(
                    open(Path(decky_plugin.DECKY_PLUGIN_DIR) / "appidmap.json")
                )["applist"]["apps"]
            }
            decky_plugin.logger.info("Initialized")
        except Exception:
            decky_plugin.logger.exception("main")
