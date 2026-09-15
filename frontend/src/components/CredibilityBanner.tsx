import React from "react";
import { DISCLAIMERS } from "../copy/strings";

export function CredibilityBanner({ state }: { state: string }) {
  if (state === "VERIFIED") return null;
  if (state === "UNVERIFIED") {
    return (
      <div className="banner banner-amber" data-testid="cred-banner-unverified">
        {DISCLAIMERS.DISC_UNVERIFIED}
      </div>
    );
  }
  return (
    <div className="banner banner-red" data-testid="cred-banner-failed">
      FAILED — numerical credibility checks did not pass. Numbers hidden behind the debug toggle.
    </div>
  );
}
