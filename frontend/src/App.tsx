import { Box } from "@mui/material";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import RequireAuth from "./components/RequireAuth";
import { useBootstrapAuth } from "./api/auth";

import Home from "./pages/Home";
import Search from "./pages/Search";
import ProviderDetail from "./pages/ProviderDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CustomerBookings from "./pages/CustomerBookings";
import ProviderDashboard from "./pages/ProviderDashboard";
import ChatPage from "./pages/ChatPage";
import AdminAnalytics from "./pages/AdminAnalytics";
import NotFound from "./pages/NotFound";

export default function App() {
  useBootstrapAuth();

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/providers/:id" element={<ProviderDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/bookings"
            element={
              <RequireAuth roles={["customer"]}>
                <CustomerBookings />
              </RequireAuth>
            }
          />
          <Route
            path="/dashboard"
            element={
              <RequireAuth roles={["provider"]}>
                <ProviderDashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/chat/:conversationId?"
            element={
              <RequireAuth roles={["customer", "provider"]}>
                <ChatPage />
              </RequireAuth>
            }
          />
          <Route
            path="/admin"
            element={
              <RequireAuth roles={["admin"]}>
                <AdminAnalytics />
              </RequireAuth>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Box>
      <Footer />
    </Box>
  );
}
