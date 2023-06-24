import {
  ButtonItem,
  definePlugin,
  DialogButton,
  Menu,
  MenuItem,
  PanelSection,
  PanelSectionRow,
  Router,
  ServerAPI,
  showContextMenu,
  staticClasses,
} from "decky-frontend-lib";
import { VFC, useState } from "react";
import { HiOutlineCamera } from "react-icons/hi";
import logo from "../assets/logo.png";

const Content: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  const [buttonEnabled, setButtonEnabled] = useState<boolean>(true);
  const [feedbackText, setFeedbackText] = useState<string>("");

  const onClick = async () => {
    setButtonEnabled(false);
    setFeedbackText("Aggregating...");
    const result = await serverAPI.callPluginMethod(
      "aggregate_all", { allapps: window.appStore.allApps.map((i: any) => [i.appid, i.display_name])});
    if (result.result >= 0) {
      setFeedbackText("Copied " + result.result + " files");
    } else {
      setFeedbackText("Something went wrong during aggregation. Please check logs.");
    }
    setButtonEnabled(true);
  };

  console.log("router");
  console.log(Router);

  return (
    <PanelSection title="Panel Section">
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={onClick} disabled={!buttonEnabled}>Aggregate!</ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <div>{feedbackText}</div>
      </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  let input_register = window.SteamClient.Input.RegisterForControllerStateChanges(async (val: any[]) => {
      /*
      R2 0
      L2 1
      R1 2
      R2 3
      Y  4
      B  5
      X  6
      A  7
      UP 8
      Right 9
      Left 10
      Down 11
      Select 12
      Steam 13
      Start 14
      QAM  ???
      L5 15
      R5 16*/
      for (const inputs of val) {
        if (Date.now() - this.pressedAt < 2000) {
          continue;
        }
        if (inputs.ulButtons && inputs.ulButtons & (1 << 13) && inputs.ulButtons & (1 << 2)) {
          (Router as any).DisableHomeAndQuickAccessButtons();
          setTimeout(() => {
            (Router as any).EnableHomeAndQuickAccessButtons();
          }, 1000);
          await serverApi.callPluginMethod("set_current_app_name", { app_name: Router.MainRunningApp?.display_name})
          console.log("in shortcut");
        }
      }
  });
  serverApi.callPluginMethod("set_id_map_fronend", {allapps: window.appStore.allApps.map((i: any) => [i.appid, i.display_name])});
  let screenshot_register = window.SteamClient.GameSessions.RegisterForScreenshotNotification(async (data: any) => {
    console.log(data);
    let res = await serverApi.callPluginMethod("copy_screenshot", { app_id: data.unAppID, url: data.details.strUrl});
    if (res.result) {
      await serverApi.toaster.toast({
        title: "Shotty",
        body: "Screenshot Symlinked",
        duration: 1000,
        critical: true
      })
    }
    else {
      await serverApi.toaster.toast({
        title: "Shotty",
        body: "Something went wrong with the screenshot",
        duration: 1000,
        critical: true
      })
    }
  });

  return {
    title: <div className={staticClasses.Title}>Screentshot Aggregator</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <HiOutlineCamera />,
    onDismount() {
      screenshot_register.unregister();
    },
  };
});
