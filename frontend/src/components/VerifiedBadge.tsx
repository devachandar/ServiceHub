import VerifiedIcon from "@mui/icons-material/Verified";
import { Chip } from "@mui/material";

export default function VerifiedBadge({ status }: { status: string }) {
  if (status !== "verified") return null;
  return (
    <Chip
      size="small"
      icon={<VerifiedIcon sx={{ fontSize: 16 }} />}
      label="Verified"
      sx={{
        bgcolor: "verified.light",
        color: "verified.dark",
        "& .MuiChip-icon": { color: "verified.dark" },
      }}
    />
  );
}
