import { useState } from "react";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  Container,
  Link,
  Paper,
  Stack,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { useRegister } from "../api/auth";
import { Role } from "../types";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("customer");
  const register = useRegister();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await register.mutateAsync({ fullName, email, password, role });
      navigate(role === "provider" ? "/dashboard" : "/");
    } catch {
      // surfaced via register.isError
    }
  }

  return (
    <Container maxWidth="xs" sx={{ py: 8 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Create an account
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Customers book services. Providers list and manage their business.
        </Typography>

        {register.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {(register.error as any)?.response?.data?.error || "Could not create your account."}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
          <Stack gap={2}>
            <ToggleButtonGroup exclusive fullWidth value={role} onChange={(_, v) => v && setRole(v)} color="primary">
              <ToggleButton value="customer">I need a service</ToggleButton>
              <ToggleButton value="provider">I offer a service</ToggleButton>
            </ToggleButtonGroup>
            <TextField label="Full name" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
            <TextField label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
            <TextField
              label="Password"
              type="password"
              required
              inputProps={{ minLength: 8 }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button type="submit" variant="contained" size="large" disabled={register.isPending}>
              {register.isPending ? "Creating account..." : "Create account"}
            </Button>
          </Stack>
        </Box>

        <Typography variant="body2" sx={{ mt: 3, textAlign: "center" }}>
          Already have an account? <Link component={RouterLink} to="/login">Sign in</Link>
        </Typography>
      </Paper>
    </Container>
  );
}
