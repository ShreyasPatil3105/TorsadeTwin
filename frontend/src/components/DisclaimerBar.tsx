import React from "react";
import { DISCLAIMERS } from "../copy/strings";

export function DisclaimerBar({ text }: { text: string }) {
  return (
    <div className="disclaimer-bar" data-testid="disclaimer-bar">
      {text}
    </div>
  );
}

export function GlobalDisclaimer() {
  return <DisclaimerBar text={DISCLAIMERS.DISC_GLOBAL} />;
}
