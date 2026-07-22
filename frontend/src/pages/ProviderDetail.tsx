import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Grid,
  MenuItem,
  Rating,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import VerifiedBadge from "../components/VerifiedBadge";
import { useProvider, useAvailability } from "../api/providers";
import { useCreateBooking } from "../api/bookings";
import { useProviderReviews } from "../api/reviews";
import { useStartConversation } from "../api/chat";
import { useAppSelector } from "../app/hooks";

export default function ProviderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = useAppSelector((s) => s.auth.user);
  const { data: provider, isLoading } = useProvider(id);
  const { data: reviews } = useProviderReviews(id);

  const [serviceId, setServiceId] = useState("");
  const [date, setDate] = useState("");
  const { data: slots, isFetching: loadingSlots } = useAvailability(id, serviceId, date);

  const createBooking = useCreateBooking();
  const startConversation = useStartConversation();

  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }
  if (!provider) return <Container sx={{ py: 6 }}>Provider not found.</Container>;

  async function handleBook(startTime: string) {
    if (!user) return navigate("/login");
    await createBooking.mutateAsync({ providerId: id!, serviceId, startTime });
    navigate("/bookings");
  }

  async function handleMessage() {
    if (!user) return navigate("/login");
    const conversation = await startConversation.mutateAsync({ providerId: id! });
    navigate(`/chat/${conversation.id}`);
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
        <Box>
          <Stack direction="row" alignItems="center" gap={1}>
            <Typography variant="h4">{provider.business_name}</Typography>
            <VerifiedBadge status={provider.verification_status} />
          </Stack>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            {provider.category} · {provider.city}, {provider.state}
          </Typography>
          <Stack direction="row" alignItems="center" gap={1} sx={{ mt: 1 }}>
            <Rating value={provider.average_rating} precision={0.5} readOnly />
            <Typography variant="body2" color="text.secondary">
              {provider.average_rating.toFixed(1)} ({provider.review_count} reviews)
            </Typography>
          </Stack>
        </Box>
        {user?.role !== "provider" && (
          <Button variant="outlined" startIcon={<ChatBubbleOutlineIcon />} onClick={handleMessage}>
            Message
          </Button>
        )}
      </Stack>

      {provider.bio && (
        <Typography sx={{ mt: 3, maxWidth: 720 }} color="text.secondary">
          {provider.bio}
        </Typography>
      )}

      <Grid container spacing={4} sx={{ mt: 1 }}>
        <Grid item xs={12} md={7}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Services
          </Typography>
          <Stack gap={1.5}>
            {provider.services.filter((s) => s.active).map((s) => (
              <Card key={s.id} variant={serviceId === s.id ? "elevation" : "outlined"}>
                <CardContent sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Box>
                    <Typography sx={{ fontWeight: 600 }}>{s.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {s.duration_minutes} min · {s.description}
                    </Typography>
                  </Box>
                  <Stack alignItems="flex-end" gap={0.5}>
                    <Typography sx={{ fontWeight: 600 }}>${s.price}</Typography>
                    <Button
                      size="small"
                      variant={serviceId === s.id ? "contained" : "outlined"}
                      onClick={() => setServiceId(s.id)}
                    >
                      {serviceId === s.id ? "Selected" : "Select"}
                    </Button>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>

          {reviews && reviews.length > 0 && (
            <>
              <Divider sx={{ my: 4 }} />
              <Typography variant="h6" sx={{ mb: 2 }}>
                Reviews
              </Typography>
              <Stack gap={2}>
                {reviews.map((r) => (
                  <Box key={r.id}>
                    <Rating value={r.rating} size="small" readOnly />
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {r.comment}
                    </Typography>
                    {r.provider_response && (
                      <Box sx={{ mt: 1, pl: 2, borderLeft: "2px solid", borderColor: "divider" }}>
                        <Typography variant="caption" color="text.secondary">
                          Provider response: {r.provider_response}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                ))}
              </Stack>
            </>
          )}
        </Grid>

        <Grid item xs={12} md={5}>
          <Card sx={{ p: 3, position: "sticky", top: 90 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Book an appointment
            </Typography>
            {!serviceId ? (
              <Typography color="text.secondary" variant="body2">
                Select a service to see open times.
              </Typography>
            ) : (
              <>
                <TextField
                  type="date"
                  label="Date"
                  fullWidth
                  size="small"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  sx={{ mb: 2 }}
                />
                {loadingSlots ? (
                  <CircularProgress size={20} />
                ) : slots && slots.length ? (
                  <Grid container spacing={1}>
                    {slots.map((slot) => (
                      <Grid item key={slot}>
                        <Chip
                          label={new Date(slot).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
                          onClick={() => handleBook(slot)}
                          clickable
                          color="primary"
                          variant="outlined"
                        />
                      </Grid>
                    ))}
                  </Grid>
                ) : date ? (
                  <Typography variant="body2" color="text.secondary">
                    No open times that day - try another date.
                  </Typography>
                ) : null}
              </>
            )}
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
