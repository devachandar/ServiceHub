import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client, { WS_BASE } from "./client";
import { Conversation, Message } from "../types";

export function useMyConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: async () => (await client.get<Conversation[]>("/chat/conversations")).data,
  });
}

export function useStartConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { providerId: string; bookingId?: string }) =>
      (await client.post<Conversation>("/chat/conversations/start", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });
}

export function useConversationMessages(conversationId?: string) {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: async () => (await client.get<Message[]>(`/chat/conversations/${conversationId}/messages`)).data,
    enabled: !!conversationId,
  });
}

/** Live-updates a message list over a WebSocket, falling back to nothing if
 * the connection drops - the REST history above is always the source of
 * truth on next load. */
export function useChatSocket(conversationId: string | undefined, onMessage: (message: Message) => void) {
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!conversationId) return;
    const token = localStorage.getItem("servicehub_access_token");
    const socket = new WebSocket(`${WS_BASE}/chat/${conversationId}/?token=${token}`);
    socketRef.current = socket;

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onmessage = (event) => onMessage(JSON.parse(event.data));

    return () => socket.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conversationId]);

  function send(body: string, attachmentUrl = "") {
    socketRef.current?.send(JSON.stringify({ body, attachmentUrl }));
  }

  return { connected, send };
}
