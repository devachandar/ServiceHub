import { createTheme } from "@mui/material/styles";

// Direction: "Verified Trade" - the whole product hinges on trust (verified
// providers, escrowed payment, reviews), so the palette leans on a deep,
// confident teal with a warm amber accent standing in for the verification
// checkmark/badge motif that recurs across cards, buttons, and the navbar.
const teal = {
  50: "#E9F3F1",
  100: "#C9E2DD",
  300: "#5FA79B",
  500: "#0F5E56",
  700: "#0A423C",
  900: "#062723",
};

const amber = {
  100: "#FCEBCB",
  400: "#E2A33B",
  600: "#B67C1F",
};

declare module "@mui/material/styles" {
  interface Palette {
    verified: Palette["primary"];
  }
  interface PaletteOptions {
    verified?: PaletteOptions["primary"];
  }
}

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: teal[500], dark: teal[700], light: teal[300], contrastText: "#fff" },
    secondary: { main: amber[400], dark: amber[600], contrastText: "#1B1F1E" },
    verified: { main: amber[400], dark: amber[600], light: amber[100], contrastText: "#1B1F1E" },
    background: { default: "#F7F8F7", paper: "#FFFFFF" },
    text: { primary: "#1B1F1E", secondary: "#5B655F" },
    divider: "#E1E5E2",
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    h1: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700, letterSpacing: "-0.02em" },
    h2: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700, letterSpacing: "-0.01em" },
    h3: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    h4: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    h5: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    h6: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, paddingInline: 18, paddingBlock: 9 },
        containedPrimary: { boxShadow: "none", "&:hover": { boxShadow: "none" } },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: `1px solid ${teal[100]}`,
          boxShadow: "none",
          transition: "box-shadow .15s ease, transform .15s ease",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { backgroundColor: "#FFFFFF", color: "#1B1F1E", boxShadow: "none", borderBottom: "1px solid #E1E5E2" },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 600 } },
    },
  },
});

export default theme;
