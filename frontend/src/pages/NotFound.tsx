import { Button, Container, Typography } from "@mui/material";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <Container sx={{ py: 10, textAlign: "center" }}>
      <Typography variant="overline" color="text.secondary">
        404
      </Typography>
      <Typography variant="h4" sx={{ mb: 3 }}>
        This job hasn't been posted.
      </Typography>
      <Button component={Link} to="/" variant="contained">
        Back home
      </Button>
    </Container>
  );
}
