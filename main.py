import os

import decky_plugin
from pathlib import Path
import json
import os
import subprocess
import sys
import shutil
import time

class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
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
            fname = url.split('/')[-1]
            glob_pattern = f"**/760/remote/{app_id}/screenshots/{fname}"
            decky_plugin.logger.info(glob_pattern)
            files = list(path.glob(glob_pattern))
            decky_plugin.logger.info(str(files))
            did = False
            for f in files:
                path = Plugin.make_path(self, app_id, fname)
                os.symlink(f, path)
                decky_plugin.logger.info(f"Symlinked {f} to {path}")
                did = True
            return did
        except Exception:
            decky_plugin.logger.exception(f"Copy screenshot: {app_id}, {url}")
            return False

    async def sdsa_classic(self):
        id_map = self._id_map
        do_copy = False
        if len(sys.argv) > 1 and sys.argv[1] == "copy":
            do_copy = True
        path = Path.home() / ".local/share/Steam/userdata"
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

        return total_copied

    def make_path(self, app_id, fname):
        final_path = self._dump_folder / str(self._id_map.get(app_id, app_id)) / fname
        final_path.parent.mkdir(parents=True, exist_ok=True)
        return final_path

    async def _main(self):
        try:
            subprocess.run(
                "curl https://api.steampowered.com/ISteamApps/GetAppList/v2/ > /tmp/appidmap.json",
                shell=True,
                check=True,
                capture_output=True,
            )
            self._id_map = {
                i["appid"]: i["name"]
                for i in json.load(open("/tmp/appidmap.json"))["applist"]["apps"]
            }
        except Exception:
            decky_plugin.logger.exception("main")
        decky_plugin.logger.info("Initialized")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Calling unload")
        pass

    # # Migrations that should be performed before entering `_main()`.
    # async def _migration(self):
    #     decky_plugin.logger.info("Migrating")
    #     # Here's a migration example for logs:
    #     # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
    #     decky_plugin.migrate_logs(
    #         os.path.join(
    #             decky_plugin.DECKY_USER_HOME,
    #             ".config",
    #             "decky-template",
    #             "template.log",
    #         )
    #     )
    #     # Here's a migration example for settings:
    #     # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
    #     # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
    #     decky_plugin.migrate_settings(
    #         os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
    #         os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"),
    #     )
    #     # Here's a migration example for runtime data:
    #     # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
    #     # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
    #     decky_plugin.migrate_runtime(
    #         os.path.join(decky_plugin.DECKY_HOME, "template"),
    #         os.path.join(
    #             decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"
    #         ),
    #     )
