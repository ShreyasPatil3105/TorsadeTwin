import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CredibilityBanner } from "../src/components/CredibilityBanner";
import { DisclaimerBar } from "../src/components/DisclaimerBar";
import { DISCLAIMERS } from "../src/copy/strings";

describe("credibility rendering", () => {
  it("renders no banner when VERIFIED", () => {
    const { container } = render(<CredibilityBanner state="VERIFIED" />);
    expect(container.querySelector(".banner")).toBeNull();
  });

  it("renders amber UNVERIFIED banner with DISC_UNVERIFIED text", () => {
    render(<CredibilityBanner state="UNVERIFIED" />);
    expect(screen.getByTestId("cred-banner-unverified")).toBeTruthy();
    expect(screen.getByText(/NOT TRUSTWORTHY/)).toBeTruthy();
  });

  it("renders red FAILED banner", () => {
    render(<CredibilityBanner state="FAILED" />);
    expect(screen.getByTestId("cred-banner-failed")).toBeTruthy();
  });

  it("disclaimer bar is always rendered with DISC_GLOBAL", () => {
    render(<DisclaimerBar text={DISCLAIMERS.DISC_GLOBAL} />);
    expect(screen.getByTestId("disclaimer-bar")).toBeTruthy();
    expect(screen.getByText(/Not clinically validated/)).toBeTruthy();
  });
});
