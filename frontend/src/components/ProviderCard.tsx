import { Box, Card, CardActionArea, CardContent, Rating, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import VerifiedBadge from "./VerifiedBadge";
import { SearchResult } from "../api/search";

export default function ProviderCard({ provider }: { provider: SearchResult }) {
  const navigate = useNavigate();
  const startingPrice = provider.services?.length
    ? Math.min(...provider.services.map((s) => Number(s.price)))
    : null;

  return (
    <Card>
      <CardActionArea onClick={() => navigate(`/providers/${provider.id}`)}>
        <Box sx={{ height: 132, bgcolor: "primary.light", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Typography variant="h4" sx={{ color: "primary.dark", opacity: 0.5 }}>
            {provider.business_name?.slice(0, 1)}
          </Typography>
        </Box>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" gap={1}>
            <Typography variant="h6" sx={{ fontSize: 17 }}>
              {provider.business_name}
            </Typography>
            <VerifiedBadge status={provider.verification_status || ""} />
          </Stack>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {provider.category} · {provider.city}, {provider.state}
          </Typography>
          <Stack direction="row" alignItems="center" gap={0.5} sx={{ mt: 1 }}>
            <Rating value={provider.average_rating || 0} precision={0.5} size="small" readOnly />
            <Typography variant="caption" color="text.secondary">
              ({provider.review_count || 0})
            </Typography>
          </Stack>
          {startingPrice != null && (
            <Typography variant="body2" sx={{ mt: 1, fontWeight: 600 }}>
              From ${startingPrice}
            </Typography>
          )}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
