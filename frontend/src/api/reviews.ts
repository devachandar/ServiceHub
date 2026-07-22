import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import client from "./client";
import { Review } from "../types";

export function useProviderReviews(providerId?: string) {
  return useQuery({
    queryKey: ["reviews", providerId],
    queryFn: async () => (await client.get<Review[]>(`/reviews/provider/${providerId}`)).data,
    enabled: !!providerId,
  });
}

export function useCreateReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (vars: { bookingId: string; rating: number; comment: string }) =>
      (await client.post<Review>("/reviews/", vars)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reviews"] }),
  });
}
