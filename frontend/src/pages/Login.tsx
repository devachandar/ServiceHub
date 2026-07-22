import { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { Alert, Box, Button, Container, Link, Paper, Stack, TextField, Typography } from "@mui/material";
import { useLogin } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login.mutateAsync({ email, password });
      navigate("/");
    } catch {
      // error surfaced below via login.isError
    }
  }

  return (
    <Container maxWidth="xs" sx={{ py: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Sign in
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Access your bookings, messages, and provider dashboard.
        </Typography>

        {login.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {(login.error as any)?.response?.data?.error || "Could not sign in."}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <Stack gap={2}>
            <TextField label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            <TextField
              label="Password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" variant="contained" size="large" disabled={login.isPending}>
              {login.isPending ? "Signing in..." : "Sign in"}
            </Button>
          </Stack>
        </Box>

        <Typography variant="body2" sx={{ mt: 3, textAlign: "center" }}>
          New to ServiceHub? <Link component={RouterLink} to="/register">Create an account</Link>
        </Typography>
      </Paper>
    </Container>
  );
}
