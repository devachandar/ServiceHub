import { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAppSelector } from "../app/hooks";
import { Role } from "../types";

export default function RequireAuth({ roles, children }: { roles?: Role[]; children: ReactElement }) {
  const { user, hydrated } = useAppSelector((s) => s.auth);

  if (!hydrated) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;

  return children;
}
