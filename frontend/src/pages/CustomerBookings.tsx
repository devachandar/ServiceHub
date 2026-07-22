import { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Rating,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useCancelBooking, useMyBookings } from "../api/bookings";
import { useInvoiceForBooking, usePayInvoice } from "../api/payments";
import { useCreateReview } from "../api/reviews";
import { Booking } from "../types";

const STATUS_COLOR: Record<string, "default" | "success" | "warning" | "error" | "info"> = {
  pending_payment: "warning",
  confirmed: "info",
  completed: "success",
  cancelled: "error",
  rescheduled: "default",
};

function BookingRow({ booking }: { booking: Booking }) {
  const { data: invoice } = useInvoiceForBooking(booking.id);
  const payInvoice = usePayInvoice();
  const cancelBooking = useCancelBooking();
  const createReview = useCreateReview();
  const [reviewOpen, setReviewOpen] = useState(false);
  const [rating, setRating] = useState<number | null>(5);
  const [comment, setComment] = useState("");

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
        <Box>
          <Typography sx={{ fontWeight: 600 }}>{booking.service_name}</Typography>
          <Typography variant="body2" color="text.secondary">
            {new Date(booking.start_time).toLocaleString()}
          </Typography>
        </Box>

        <Stack direction="row" gap={1.5} alignItems="center">
          <Chip size="small" label={booking.status.replace("_", " ")} color={STATUS_COLOR[booking.status]} />
          <Typography sx={{ fontWeight: 600 }}>${booking.price}</Typography>

          {invoice && invoice.status !== "paid" && (
            <Button size="small" variant="contained" onClick={() => payInvoice.mutate(invoice.id)} disabled={payInvoice.isPending}>
              Pay now
            </Button>
          )}
          {booking.status !== "completed" && booking.status !== "cancelled" && (
            <Button size="small" color="error" onClick={() => cancelBooking.mutate({ bookingId: booking.id })}>
              Cancel
            </Button>
          )}
          {booking.status === "completed" && (
            <Button size="small" onClick={() => setReviewOpen(true)}>
              Leave a review
            </Button>
          )}
        </Stack>
      </CardContent>

      <Dialog open={reviewOpen} onClose={() => setReviewOpen(false)} fullWidth maxWidth="xs">
        <DialogTitle>Rate your experience</DialogTitle>
        <DialogContent>
          <Rating value={rating} onChange={(_, v) => setRating(v)} sx={{ mb: 2 }} />
          <TextField
            label="Comment"
            fullWidth
            multiline
            rows={3}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviewOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={async () => {
              await createReview.mutateAsync({ bookingId: booking.id, rating: rating || 5, comment });
              setReviewOpen(false);
            }}
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
}

export default function CustomerBookings() {
  const { data: bookings, isLoading } = useMyBookings();

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        My bookings
      </Typography>
      {isLoading ? (
        <CircularProgress />
      ) : bookings && bookings.length ? (
        bookings.map((b) => <BookingRow key={b.id} booking={b} />)
      ) : (
        <Typography color="text.secondary">You don't have any bookings yet.</Typography>
      )}
    </Container>
  );
}
