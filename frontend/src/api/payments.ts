import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Invoice } from "../types";

export function useInvoiceForBooking(bookingId?: string) {
  return useQuery({
    queryKey: ["invoice", bookingId],
    queryFn: async () => {
      try {
        return (await client.get<Invoice>(`/payments/booking/${bookingId}`)).data;
      } catch {
        return null;
      }
    },
    enabled: !!bookingId,
    refetchInterval: (query) => (query.state.data?.status === "paid" ? false : 2000),
  });
}

export function usePayInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (invoiceId: string) => (await client.post(`/payments/${invoiceId}/pay`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["invoice"] }),
  });
}

export function useProviderEarnings() {
  return useQuery({
    queryKey: ["earnings"],
    queryFn: async () =>
      (
        await client.get<{ grossEarnings: string; platformFees: string; netEarnings: string; paidInvoiceCount: number }>(
          "/payments/provider/earnings"
        )
      ).data,
  });
}
