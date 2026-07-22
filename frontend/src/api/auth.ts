import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { useAppDispatch } from "../app/hooks";
import { hydrationFinished, loggedOut, sessionEstablished } from "../features/auth/authSlice";
import { AuthUser, Role } from "../types";

interface SessionResponse {
  user: AuthUser;
  accessToken: string;
  refreshToken: string;
}

export function useBootstrapAuth() {
  const dispatch = useAppDispatch();
  const token = localStorage.getItem("servicehub_access_token");

  return useQuery({
    queryKey: ["auth", "bootstrap"],
    queryFn: async () => {
      if (!token) {
        dispatch(hydrationFinished(null));
        return null;
      }
      try {
        const res = await client.get<AuthUser>("/auth/me");
        dispatch(hydrationFinished(res.data));
        return res.data;
      } catch {
        dispatch(hydrationFinished(null));
        return null;
      }
    },
  });
}

export function useLogin() {
  const dispatch = useAppDispatch();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { email: string; password: string }) => {
      const res = await client.post<SessionResponse>("/auth/login", vars);
      return res.data;
    },
    onSuccess: (data) => {
      dispatch(sessionEstablished(data));
      qc.invalidateQueries();
    },
  });
}

export function useRegister() {
  const dispatch = useAppDispatch();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { email: string; password: string; fullName: string; role: Role }) => {
      const res = await client.post<SessionResponse>("/auth/register", vars);
      return res.data;
    },
    onSuccess: (data) => {
      dispatch(sessionEstablished(data));
      qc.invalidateQueries();
    },
  });
}

export function useLogout() {
  const dispatch = useAppDispatch();
  return () => {
    const refreshToken = localStorage.getItem("servicehub_refresh_token");
    client.post("/auth/logout", { refreshToken }).catch(() => {});
    dispatch(loggedOut());
  };
}
