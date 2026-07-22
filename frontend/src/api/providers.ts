import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Provider } from "../types";

export function useProvider(providerId?: string) {
  return useQuery({
    queryKey: ["provider", providerId],
    queryFn: async () => (await client.get<Provider>(`/providers/${providerId}`)).data,
    enabled: !!providerId,
  });
}

export function useMyProviderProfile() {
  return useQuery({
    queryKey: ["provider", "me"],
    queryFn: async () => {
      try {
        return (await client.get<Provider>("/providers/me")).data;
      } catch {
        return null;
      }
    },
  });
}

export function useOnboardProvider() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { businessName: string; bio: string; category: string; city: string; state: string }) =>
      (await client.post<Provider>("/providers/onboard", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["provider", "me"] }),
  });
}

export function useAddService() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { name: string; description: string; price: number; duration_minutes: number }) =>
      (await client.post("/providers/me/services", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["provider", "me"] }),
  });
}

export function useSetWorkingHours() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (entries: { weekday: number; startTime: string; endTime: string }[]) =>
      (await client.put("/providers/me/working-hours", entries)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["provider", "me"] }),
  });
}

export function useAvailability(providerId?: string, serviceId?: string, date?: string) {
  return useQuery({
    queryKey: ["availability", providerId, serviceId, date],
    queryFn: async () =>
      (await client.get<{ slots: string[] }>(`/bookings/availability/${providerId}`, { params: { serviceId, date } }))
        .data.slots,
    enabled: !!providerId && !!serviceId && !!date,
  });
}
