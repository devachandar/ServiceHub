import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, Container, Grid, Typography } from "@mui/material";
import client from "../api/client";

interface KPIResponse {
  totals: {
    bookings_created: number;
    bookings_completed: number;
    bookings_cancelled: number;
    revenue: string;
    new_reviews: number;
    new_users: number;
  };
}

export default function AdminAnalytics() {
  const { data } = useQuery({
    queryKey: ["kpis"],
    queryFn: async () => (await client.get<KPIResponse>("/analytics/kpis")).data,
  });

  const cards = data
    ? [
        ["New users (30d)", data.totals.new_users],
        ["Bookings created", data.totals.bookings_created],
        ["Bookings completed", data.totals.bookings_completed],
        ["Bookings cancelled", data.totals.bookings_cancelled],
        ["Revenue", `$${data.totals.revenue}`],
        ["New reviews", data.totals.new_reviews],
      ]
    : [];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Platform analytics
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Trailing 30 days, aggregated by Analytics Service from booking/payment/review events.
      </Typography>
      <Grid container spacing={2}>
        {cards.map(([label, value]) => (
          <Grid item xs={12} sm={6} md={4} key={label as string}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="caption" color="text.secondary">
                  {label}
                </Typography>
                <Typography variant="h4">{value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
