import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Box,
  Container,
  Grid,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
  CircularProgress,
} from "@mui/material";
import ProviderCard from "../components/ProviderCard";
import { useSearch } from "../api/search";

export default function Search() {
  const [params] = useSearchParams();
  const [q, setQ] = useState(params.get("q") || "");
  const [category, setCategory] = useState(params.get("category") || "");
  const [city, setCity] = useState("");
  const [sort, setSort] = useState("relevance");

  const { data, isLoading, isError } = useSearch({ q, category, city, sort });

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        {data ? `${data.total} providers found` : "Find a pro"}
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction={{ xs: "column", sm: "row" }} gap={2}>
          <TextField label="Keyword" fullWidth size="small" value={q} onChange={(e) => setQ(e.target.value)} />
          <TextField label="City" fullWidth size="small" value={city} onChange={(e) => setCity(e.target.value)} />
          <TextField
            label="Category"
            fullWidth
            size="small"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
          <Select size="small" value={sort} onChange={(e) => setSort(e.target.value)} sx={{ minWidth: 160 }}>
            <MenuItem value="relevance">Relevance</MenuItem>
            <MenuItem value="rating">Top rated</MenuItem>
            <MenuItem value="newest">Newest</MenuItem>
          </Select>
        </Stack>
      </Paper>

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : isError ? (
        <Typography color="text.secondary">
          Search is temporarily unavailable - make sure search-service and Elasticsearch are running.
        </Typography>
      ) : data && data.results.length ? (
        <Grid container spacing={2}>
          {data.results.map((p) => (
            <Grid item xs={12} sm={6} md={4} key={p.id}>
              <ProviderCard provider={p} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Typography color="text.secondary">No providers match those filters yet.</Typography>
      )}
    </Container>
  );
}
