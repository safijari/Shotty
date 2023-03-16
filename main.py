import os

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin
from pathlib import Path
import json
import os
import subprocess
import sys
import shutil


async def sdsa_classic():
    do_copy = False
    if len(sys.argv) > 1 and sys.argv[1] == "copy":
        do_copy = True
    path = Path.home() / ".local/share/Steam/userdata"
    files = list(path.glob("**/screenshots/*.jpg"))

    subprocess.run(
        "curl https://api.steampowered.com/ISteamApps/GetAppList/v2/ > /tmp/appidmap.json",
        shell=True,
        check=True,
        capture_output=True,
    )

    id_map = {
        i["appid"]: i["name"]
        for i in json.load(open("/tmp/appidmap.json"))["applist"]["apps"]
    }

    dump_folder = Path.home() / "Pictures" / "Screenshots"

    total_copied = 0

    for f in files:
        appid = int(f.parent.parent.name)
        name = str(id_map.get(appid, appid))
        final_path = dump_folder / name / f.name
        final_path.parent.mkdir(parents=True, exist_ok=True)
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


class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def aggregate_all(self):
        try:
            res = await sdsa_classic()
            decky_plugin.logger.debug(f"Copied {res} files")
        except Exception:
            decky_plugin.logger.exception("could not")
            return -1

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky_plugin.logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Goodbye World!")
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
