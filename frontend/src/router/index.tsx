import { createBrowserRouter } from "react-router-dom";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { Dashboard } from "../pages/Dashboard";
import { CompanyDirectory } from "../pages/CompanyDirectory";
import { CompanyProfile } from "../pages/CompanyProfile";
import { GlobalNews } from "../pages/GlobalNews";
import { AdminDashboard } from "../pages/AdminDashboard";
import { Evaluation } from "../pages/Evaluation";
import { GlobalError } from "../components/GlobalError";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <DashboardLayout />,
    errorElement: <GlobalError />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: "companies",
        element: <CompanyDirectory />,
      },
      {
        path: "companies/:slug",
        element: <CompanyProfile />,
      },
      {
        path: "news",
        element: <GlobalNews />,
      },
      {
        path: "admin",
        element: <AdminDashboard />,
      },
      {
        path: "evaluation",
        element: <Evaluation />,
      }
    ],
  },
]);
