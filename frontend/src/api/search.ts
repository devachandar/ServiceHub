import { useQuery } from "@tanstack/react-query";
import client from "./client";
import { Provider } from "../types";

export interface SearchFilters {
  q?: string;
  category?: string;
  city?: string;
  minRating?: string;
  sort?: string;
  page?: number;
}

export interface SearchResult extends Partial<Provider> {
  id: string;
  score: number;
}

export function useSearch(filters: SearchFilters) {
  const cleaned = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== "" && v != null));
  return useQuery({
    queryKey: ["search", cleaned],
    queryFn: async () =>
      (await client.get<{ total: number; results: SearchResult[] }>("/search", { params: cleaned })).data,
  });
}
