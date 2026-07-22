import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useAddService, useMyProviderProfile, useOnboardProvider, useSetWorkingHours } from "../api/providers";
import { useCompleteBooking, useProviderBookings } from "../api/bookings";
import { useProviderEarnings } from "../api/payments";
import VerifiedBadge from "../components/VerifiedBadge";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function ProfileTab() {
  const { data: provider } = useMyProviderProfile();
  const onboard = useOnboardProvider();
  const [form, setForm] = useState({ businessName: "", bio: "", category: "", city: "", state: "" });

  if (provider) {
    return (
      <Box>
        <Stack direction="row" alignItems="center" gap={1.5} sx={{ mb: 1 }}>
          <Typography variant="h6">{provider.business_name}</Typography>
          <VerifiedBadge status={provider.verification_status} />
          {provider.verification_status !== "verified" && (
            <Chip size="small" label={provider.verification_status.replace("_", " ")} />
          )}
        </Stack>
        <Typography color="text.secondary">
          {provider.category} · {provider.city}, {provider.state}
        </Typography>
        {provider.verification_status === "unverified" && (
          <Alert severity="info" sx={{ mt: 2, maxWidth: 480 }}>
            Submit your verification documents so an admin can approve your profile and make it bookable.
          </Alert>
        )}
      </Box>
    );
  }

  return (
    <Box component="form" sx={{ maxWidth: 420 }} onSubmit={(e) => { e.preventDefault(); onboard.mutate(form as any); }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Set up your business profile
      </Typography>
      <Stack gap={2}>
        <TextField label="Business name" required value={form.businessName} onChange={(e) => setForm({ ...form, businessName: e.target.value })} />
        <TextField label="Category" required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
        <TextField label="Bio" multiline rows={3} value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
        <TextField label="City" required value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
        <TextField label="State" required value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
        <Button type="submit" variant="contained" disabled={onboard.isPending}>
          {onboard.isPending ? "Saving..." : "Create profile"}
        </Button>
      </Stack>
    </Box>
  );
}

function ServicesTab() {
  const { data: provider } = useMyProviderProfile();
  const addService = useAddService();
  const [form, setForm] = useState({ name: "", description: "", price: "", duration_minutes: "60" });

  return (
    <Grid container spacing={4}>
      <Grid item xs={12} md={5}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Add a service
        </Typography>
        <Stack gap={2} sx={{ maxWidth: 360 }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <TextField label="Description" multiline rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <TextField label="Price (USD)" type="number" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
          <TextField label="Duration (minutes)" type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })} />
          <Button
            variant="contained"
            onClick={() =>
              addService.mutate({
                name: form.name,
                description: form.description,
                price: Number(form.price),
                duration_minutes: Number(form.duration_minutes),
              })
            }
          >
            Add service
          </Button>
        </Stack>
      </Grid>
      <Grid item xs={12} md={7}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Your services
        </Typography>
        <Stack gap={1.5}>
          {provider?.services.map((s) => (
            <Card key={s.id} variant="outlined">
              <CardContent sx={{ display: "flex", justifyContent: "space-between" }}>
                <Box>
                  <Typography sx={{ fontWeight: 600 }}>{s.name}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {s.duration_minutes} min
                  </Typography>
                </Box>
                <Typography sx={{ fontWeight: 600 }}>${s.price}</Typography>
              </CardContent>
            </Card>
          ))}
        </Stack>
      </Grid>
    </Grid>
  );
}

function HoursTab() {
  const { data: provider } = useMyProviderProfile();
  const setHours = useSetWorkingHours();
  const [hours, setHoursState] = useState(
    WEEKDAYS.map((_, i) => ({ weekday: i, startTime: "09:00", endTime: "17:00", enabled: i < 5 }))
  );

  return (
    <Box sx={{ maxWidth: 480 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Weekly availability
      </Typography>
      <Stack gap={1.5}>
        {hours.map((h, i) => (
          <Stack key={h.weekday} direction="row" alignItems="center" gap={2}>
            <Chip
              label={WEEKDAYS[h.weekday]}
              color={h.enabled ? "primary" : "default"}
              onClick={() => setHoursState((prev) => prev.map((p, j) => (j === i ? { ...p, enabled: !p.enabled } : p)))}
              sx={{ width: 56 }}
            />
            <TextField
              type="time"
              size="small"
              disabled={!h.enabled}
              value={h.startTime}
              onChange={(e) => setHoursState((prev) => prev.map((p, j) => (j === i ? { ...p, startTime: e.target.value } : p)))}
            />
            <TextField
              type="time"
              size="small"
              disabled={!h.enabled}
              value={h.endTime}
              onChange={(e) => setHoursState((prev) => prev.map((p, j) => (j === i ? { ...p, endTime: e.target.value } : p)))}
            />
          </Stack>
        ))}
        <Button
          variant="contained"
          sx={{ mt: 1, alignSelf: "flex-start" }}
          onClick={() =>
            setHours.mutate(
              hours.filter((h) => h.enabled).map((h) => ({ weekday: h.weekday, startTime: `${h.startTime}:00`, endTime: `${h.endTime}:00` }))
            )
          }
        >
          Save schedule
        </Button>
      </Stack>
      {!provider && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Create your business profile in the Profile tab first.
        </Alert>
      )}
    </Box>
  );
}

function BookingsTab() {
  const { data: bookings } = useProviderBookings();
  const complete = useCompleteBooking();

  return (
    <Stack gap={1.5}>
      {bookings?.length ? (
        bookings.map((b) => (
          <Card key={b.id} variant="outlined">
            <CardContent sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 1 }}>
              <Box>
                <Typography sx={{ fontWeight: 600 }}>{b.service_name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(b.start_time).toLocaleString()}
                </Typography>
              </Box>
              <Stack direction="row" gap={1} alignItems="center">
                <Chip size="small" label={b.status.replace("_", " ")} />
                {b.status === "confirmed" && (
                  <Button size="small" variant="contained" onClick={() => complete.mutate(b.id)}>
                    Mark completed
                  </Button>
                )}
              </Stack>
            </CardContent>
          </Card>
        ))
      ) : (
        <Typography color="text.secondary">No bookings yet.</Typography>
      )}
    </Stack>
  );
}

function EarningsTab() {
  const { data } = useProviderEarnings();
  if (!data) return null;
  return (
    <Grid container spacing={2} sx={{ maxWidth: 640 }}>
      {[
        ["Gross earnings", data.grossEarnings],
        ["Platform fees", data.platformFees],
        ["Net earnings", data.netEarnings],
        ["Paid bookings", String(data.paidInvoiceCount)],
      ].map(([label, value]) => (
        <Grid item xs={6} key={label}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="caption" color="text.secondary">
                {label}
              </Typography>
              <Typography variant="h5">{label === "Paid bookings" ? value : `$${value}`}</Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default function ProviderDashboard() {
  const [tab, setTab] = useState(0);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Provider dashboard
      </Typography>
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Profile" />
        <Tab label="Services" />
        <Tab label="Hours" />
        <Tab label="Bookings" />
        <Tab label="Earnings" />
      </Tabs>
      {tab === 0 && <ProfileTab />}
      {tab === 1 && <ServicesTab />}
      {tab === 2 && <HoursTab />}
      {tab === 3 && <BookingsTab />}
      {tab === 4 && <EarningsTab />}
    </Container>
  );
}
