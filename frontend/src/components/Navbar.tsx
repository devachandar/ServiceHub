import { AppBar, Box, Button, Toolbar, Typography, Avatar, Stack } from "@mui/material";
import HandymanIcon from "@mui/icons-material/Handyman";
import { Link, useNavigate } from "react-router-dom";
import { useAppSelector } from "../app/hooks";
import { useLogout } from "../api/auth";

export default function Navbar() {
  const user = useAppSelector((s) => s.auth.user);
  const logout = useLogout();
  const navigate = useNavigate();

  return (
    <AppBar position="sticky">
      <Toolbar sx={{ maxWidth: 1180, width: "100%", mx: "auto" }}>
        <Stack direction="row" alignItems="center" gap={1} sx={{ flexGrow: 1 }}>
          <Box
            component={Link}
            to="/"
            sx={{ display: "flex", alignItems: "center", gap: 1, textDecoration: "none", color: "inherit" }}
          >
            <HandymanIcon sx={{ color: "secondary.main" }} />
            <Typography variant="h6" sx={{ fontSize: 20 }}>
              ServiceHub
            </Typography>
          </Box>
        </Stack>

        <Stack direction="row" gap={1.5} alignItems="center">
          <Button component={Link} to="/search" color="inherit">
            Find a pro
          </Button>
          {user?.role === "provider" && (
            <Button component={Link} to="/dashboard" color="inherit">
              Dashboard
            </Button>
          )}
          {user?.role === "customer" && (
            <Button component={Link} to="/bookings" color="inherit">
              My bookings
            </Button>
          )}
          {user?.role === "admin" && (
            <Button component={Link} to="/admin" color="inherit">
              Admin
            </Button>
          )}

          {user ? (
            <>
              <Avatar sx={{ width: 30, height: 30, bgcolor: "primary.main", fontSize: 14 }}>
                {user.full_name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
              </Avatar>
              <Button
                variant="outlined"
                size="small"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Button component={Link} to="/login" color="inherit">
                Sign in
              </Button>
              <Button component={Link} to="/register" variant="contained" color="primary">
                Get started
              </Button>
            </>
          )}
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
