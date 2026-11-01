import { Badge, Button, createTheme, SegmentedControl, TextInput } from "@mantine/core";
import { DatePickerInput } from "@mantine/dates";
import { SLATE_DARK, SLATE_GRAY, TESSIO_BLUE } from "./mantine-colors.constant";

const SANS_FONT = "var(--font-geist-sans), system-ui, sans-serif";

export const mantineTheme = createTheme({
  primaryColor: "tessio",
  primaryShade: { light: 6, dark: 6 },
  autoContrast: true,
  respectReducedMotion: true,
  cursorType: "pointer",
  colors: {
    tessio: TESSIO_BLUE,
    gray: SLATE_GRAY,
    dark: SLATE_DARK,
  },
  fontFamily: SANS_FONT,
  fontFamilyMonospace: "var(--font-geist-mono), ui-monospace, monospace",
  headings: { fontFamily: SANS_FONT, fontWeight: "600" },
  fontSizes: { xs: "12px", sm: "14px", md: "16px", lg: "20px", xl: "24px" },
  radius: { xs: "4px", sm: "6px", md: "10px", lg: "14px", xl: "20px" },
  defaultRadius: "md",
  spacing: { xs: "8px", sm: "12px", md: "16px", lg: "24px", xl: "32px" },
  components: {
    Button: Button.extend({ defaultProps: { size: "sm" } }),
    TextInput: TextInput.extend({ defaultProps: { size: "sm" } }),
    DatePickerInput: DatePickerInput.extend({ defaultProps: { size: "sm" } }),
    SegmentedControl: SegmentedControl.extend({ defaultProps: { size: "sm" } }),
    Badge: Badge.extend({ defaultProps: { radius: "xl", tt: "none" } }),
  },
});
