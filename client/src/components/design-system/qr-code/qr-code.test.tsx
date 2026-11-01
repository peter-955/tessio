import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { axe } from "vitest-axe";
import { DSQrCode } from "./qr-code";

const SETUP_URI = "otpauth://totp/Tessio:jane%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=Tessio";

describe("DSQrCode", () => {
  it("renders an svg inside an element with role img and the given label", async () => {
    const { container } = render(<DSQrCode value={SETUP_URI} ariaLabel="Scan this QR code" />);

    expect(await axe(container)).toHaveNoViolations();

    const image = screen.getByRole("img", { name: "Scan this QR code" });

    expect(image.querySelector("svg")).not.toBeNull();
    expect(image.querySelector("svg")).toHaveAttribute("width", "192");
  });
});
