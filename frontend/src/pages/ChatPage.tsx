import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Box,
  Container,
  Divider,
  Grid,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  TextField,
  IconButton,
  Typography,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { useChatSocket, useConversationMessages, useMyConversations } from "../api/chat";
import { useAppSelector } from "../app/hooks";
import { Message } from "../types";

export default function ChatPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const user = useAppSelector((s) => s.auth.user);
  const { data: conversations } = useMyConversations();
  const { data: history } = useConversationMessages(conversationId);
  const [liveMessages, setLiveMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");

  useEffect(() => setLiveMessages([]), [conversationId]);

  const { send } = useChatSocket(conversationId, (message) => setLiveMessages((prev) => [...prev, message]));

  const allMessages = [...(history || []), ...liveMessages];

  function handleSend() {
    if (!draft.trim()) return;
    send(draft.trim());
    setDraft("");
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Messages
      </Typography>
      <Grid container component={Paper} sx={{ height: 560 }}>
        <Grid item xs={4} sx={{ borderRight: "1px solid", borderColor: "divider", overflowY: "auto" }}>
          <List disablePadding>
            {conversations?.map((c) => (
              <ListItemButton key={c.id} selected={c.id === conversationId} onClick={() => navigate(`/chat/${c.id}`)}>
                <ListItemText
                  primary={`Conversation ${c.id.slice(0, 8)}`}
                  secondary={c.last_message?.body || "No messages yet"}
                  secondaryTypographyProps={{ noWrap: true }}
                />
              </ListItemButton>
            ))}
            {!conversations?.length && (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                Message a provider from their profile page to start a conversation.
              </Typography>
            )}
          </List>
        </Grid>

        <Grid item xs={8} sx={{ display: "flex", flexDirection: "column" }}>
          <Box sx={{ flexGrow: 1, overflowY: "auto", p: 2 }}>
            {conversationId ? (
              allMessages.map((m) => (
                <Box
                  key={m.id}
                  sx={{ display: "flex", justifyContent: m.sender_id === user?.id ? "flex-end" : "flex-start", mb: 1 }}
                >
                  <Box
                    sx={{
                      bgcolor: m.sender_id === user?.id ? "primary.main" : "grey.100",
                      color: m.sender_id === user?.id ? "#fff" : "text.primary",
                      px: 1.5,
                      py: 1,
                      borderRadius: 2,
                      maxWidth: "70%",
                    }}
                  >
                    <Typography variant="body2">{m.body}</Typography>
                  </Box>
                </Box>
              ))
            ) : (
              <Typography color="text.secondary">Select a conversation to view messages.</Typography>
            )}
          </Box>
          {conversationId && (
            <>
              <Divider />
              <Stack direction="row" gap={1} sx={{ p: 1.5 }}>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Type a message"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                />
                <IconButton color="primary" onClick={handleSend}>
                  <SendIcon />
                </IconButton>
              </Stack>
            </>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}
