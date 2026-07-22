import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Booking } from "../types";

export function useMyBookings() {
  return useQuery({
    queryKey: ["bookings", "mine"],
    queryFn: async () => (await client.get<Booking[]>("/bookings/mine")).data,
  });
}

export function useProviderBookings() {
  return useQuery({
    queryKey: ["bookings", "provider"],
    queryFn: async () => (await client.get<Booking[]>("/bookings/provider")).data,
  });
}

export function useCreateBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { providerId: string; serviceId: string; startTime: string }) =>
      (await client.post<Booking>("/bookings/", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bookings"] }),
  });
}

export function useCancelBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { bookingId: string; reason?: string }) =>
      (await client.patch<Booking>(`/bookings/${vars.bookingId}/cancel`, { reason: vars.reason })).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bookings"] }),
  });
}

export function useCompleteBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (bookingId: string) => (await client.patch<Booking>(`/bookings/${bookingId}/complete`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bookings"] }),
  });
}
