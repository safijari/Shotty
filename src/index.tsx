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
import { HiOutlineCamera } from "react-icons/fa";
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
  serverApi.callPluginMethod("set_id_map_fronend", {allapps: window.appStore.allApps.map((i: any) => [i.appid, i.display_name])});
  let screenshot_register = window.SteamClient.GameSessions.RegisterForScreenshotNotification(async (data: any) => {
    let res = await serverApi.callPluginMethod("copy_screenshot", { app_id: data.unAppID, url: data.details.strUrl});
    if (res.result) {
      await serverApi.toaster.toast({
        title: "Shotty",
        body: "Screenshot Symlinked",
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
