import { useState } from "react";
import { Box, Button, Container, Grid, Paper, Stack, TextField, Typography, Chip } from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import { useNavigate } from "react-router-dom";

const CATEGORIES = ["Cleaning", "Plumbing", "Electrical", "Handyman", "Moving", "Landscaping", "Painting", "Personal training"];

export default function Home() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    navigate(`/search${query ? `?q=${encodeURIComponent(query)}` : ""}`);
  }

  return (
    <>
      <Box sx={{ bgcolor: "primary.dark", color: "#fff", py: { xs: 8, md: 12 } }}>
        <Container maxWidth="lg">
          <Typography variant="overline" sx={{ color: "secondary.main", letterSpacing: 2 }}>
            ServiceHub · verified pros, booked in minutes
          </Typography>
          <Typography variant="h1" sx={{ fontSize: { xs: 34, md: 52 }, maxWidth: 640, mt: 1 }}>
            Every job done right, by someone{" "}
            <Box component="span" sx={{ color: "secondary.main" }}>
              already verified.
            </Box>
          </Typography>
          <Typography sx={{ mt: 2, maxWidth: 480, color: "rgba(255,255,255,0.8)" }}>
            Search local providers, check real reviews, book a time slot, and pay - all without leaving the page.
          </Typography>

          <Paper
            component="form"
            onSubmit={handleSearch}
            sx={{ mt: 4, p: 1, display: "flex", gap: 1, maxWidth: 560, borderRadius: 2 }}
          >
            <TextField
              fullWidth
              variant="standard"
              placeholder="What do you need done? Try “house cleaning”"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              InputProps={{ disableUnderline: true, sx: { px: 1.5 } }}
            />
            <Button type="submit" variant="contained" color="secondary" startIcon={<SearchIcon />}>
              Search
            </Button>
          </Paper>

          <Stack direction="row" gap={4} sx={{ mt: 6 }}>
            <Box>
              <Typography variant="h5">10M+</Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                CUSTOMERS SUPPORTED
              </Typography>
            </Box>
            <Box>
              <Typography variant="h5">500K+</Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                VERIFIED PROVIDERS
              </Typography>
            </Box>
            <Box>
              <Typography variant="h5">&lt;200ms</Typography>
              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)" }}>
                SEARCH LATENCY TARGET
              </Typography>
            </Box>
          </Stack>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Browse by category
        </Typography>
        <Grid container spacing={1.5}>
          {CATEGORIES.map((c) => (
            <Grid item key={c}>
              <Chip
                label={c}
                onClick={() => navigate(`/search?category=${encodeURIComponent(c.toLowerCase())}`)}
                sx={{ px: 1, py: 2.5, fontSize: 14 }}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    </>
  );
}
