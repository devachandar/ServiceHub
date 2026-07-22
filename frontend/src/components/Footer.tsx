import { Box, Container, Stack, Typography } from "@mui/material";

export default function Footer() {
  return (
    <Box component="footer" sx={{ borderTop: "1px solid", borderColor: "divider", py: 4, mt: 6 }}>
      <Container maxWidth="lg">
        <Stack direction="row" justifyContent="space-between" flexWrap="wrap" gap={1}>
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} ServiceHub - a microservices portfolio project.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Auth · User · Provider · Booking · Review · Payment · Search · Chat · Analytics
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
}
