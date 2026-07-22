export type Role = "customer" | "provider" | "admin";

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  status: "active" | "suspended";
}

export interface Service {
  id: string;
  name: string;
  description: string;
  price: string;
  duration_minutes: number;
  active: boolean;
}

export interface WorkingHours {
  weekday: number;
  start_time: string;
  end_time: string;
}

export interface Provider {
  user_id: string;
  business_name: string;
  email: string;
  bio: string;
  category: string;
  city: string;
  state: string;
  verification_status: "unverified" | "pending" | "verified" | "rejected";
  status: "active" | "paused" | "removed";
  average_rating: number;
  review_count: number;
  services: Service[];
  working_hours: WorkingHours[];
  portfolio_images: { id: string; url: string; caption: string }[];
}

export interface Booking {
  id: string;
  customer_id: string;
  provider_id: string;
  service_id: string;
  service_name: string;
  price: string;
  start_time: string;
  end_time: string;
  status: "pending_payment" | "confirmed" | "completed" | "cancelled" | "rescheduled";
  cancellation_reason: string;
  created_at: string;
}

export interface Review {
  id: string;
  booking_id: string;
  customer_id: string;
  provider_id: string;
  rating: number;
  comment: string;
  provider_response: string;
  created_at: string;
}

export interface Invoice {
  id: string;
  booking_id: string;
  amount: string;
  platform_fee: string;
  status: "pending" | "paid" | "failed" | "refunded" | "partially_refunded";
  created_at: string;
}

export interface Conversation {
  id: string;
  customer_id: string;
  provider_id: string;
  booking_id: string | null;
  last_message: Message | null;
  created_at: string;
}

export interface Message {
  id: string;
  sender_id: string;
  sender_role: Role;
  body: string;
  attachment_url: string;
  read_at: string | null;
  created_at: string;
}
