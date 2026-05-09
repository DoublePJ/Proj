import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
} from "react-router-dom";
// import './styles/responsive.css';
import './index.css';
import NavBar from './components/navBar';
import PageLanding from './pages/pageLanding';
import PageLibrary from './pages/pageLibrary';
import PageChat from './pages/pageChat';
import PageAuth from './pages/pageAuth';
import PageResetPassword from './pages/pageResetPassword';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LibraryProvider } from './contexts/LibraryContext';
import RequireAuth from './components/RequireAuth';
import 'bootstrap/dist/css/bootstrap.min.css';
import Laws from './components/laws';
import PageAccount from './pages/pageAccount';
import Jude from './components/judg';

const Layout = () => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <PageAuth />;

  return (
    <>
      <NavBar />
      <main className="landing-content">
        <Outlet />
      </main>
    </>
  );
}

const router = createBrowserRouter([
  {
    path: "/reset-password",
    element: <PageResetPassword />,
  },
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <RequireAuth><PageLanding /></RequireAuth>,
      },
      {
        path: "/chat/:chat_id",
        element: <RequireAuth><PageChat /></RequireAuth>,
      },
      {
        path: "/library",
        element: <RequireAuth><PageLibrary /></RequireAuth>,
      },
      {
        path: "/library/act",
        element: <RequireAuth><Laws /></RequireAuth>,
        children: [
          {
            path: ":act",
            children: [
              { index: true },
              {
                path: "book/:book",
                children: [
                  { index: true },
                  {
                    path: "group/:group",
                    children: [
                      { index: true },
                      {
                        path: "super_section/:super_section",
                        children: [
                          { index: true },
                          {
                            path: "section/:section",
                            element: <Laws />,
                          },
                        ],
                      },
                    ],
                  }
                ]
              }
            ]
          },
        ],
      },
      {
        path: "/library/judgment/:judgment_id",
        element: <RequireAuth><Jude /></RequireAuth>,
      },
      {
        path: "/account",
        element: <RequireAuth><PageAccount /></RequireAuth>,
      }
    ]
  }
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AuthProvider>
      <LibraryProvider>
        <RouterProvider router={router} />
      </LibraryProvider>
    </AuthProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();