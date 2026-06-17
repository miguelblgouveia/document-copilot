import { apiFetch } from "@/lib/http";

export interface CurrentUser {
  id: string;
  email: string;
}

export function getMe(): Promise<CurrentUser> {
  return apiFetch<CurrentUser>("/auth/me");
}
