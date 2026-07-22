import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { AuthUser } from "../../types";

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  hydrated: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: localStorage.getItem("servicehub_access_token"),
  hydrated: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    sessionEstablished(state, action: PayloadAction<{ user: AuthUser; accessToken: string; refreshToken?: string }>) {
      state.user = action.payload.user;
      state.accessToken = action.payload.accessToken;
      localStorage.setItem("servicehub_access_token", action.payload.accessToken);
      if (action.payload.refreshToken) {
        localStorage.setItem("servicehub_refresh_token", action.payload.refreshToken);
      }
    },
    hydrationFinished(state, action: PayloadAction<AuthUser | null>) {
      state.user = action.payload;
      state.hydrated = true;
      if (!action.payload) {
        state.accessToken = null;
      }
    },
    loggedOut(state) {
      state.user = null;
      state.accessToken = null;
      localStorage.removeItem("servicehub_access_token");
      localStorage.removeItem("servicehub_refresh_token");
    },
  },
});

export const { sessionEstablished, hydrationFinished, loggedOut } = authSlice.actions;
export default authSlice.reducer;
