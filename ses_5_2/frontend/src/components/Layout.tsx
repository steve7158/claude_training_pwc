import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/documents", label: "Documents" },
  { to: "/upload", label: "Upload" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-8">
            <span className="text-lg font-bold text-carta-700">Carta Healthcare</span>
            <nav className="flex gap-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `text-sm font-medium ${isActive ? "text-carta-600" : "text-slate-500 hover:text-slate-800"}`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-600">
              {user?.full_name} <span className="text-slate-400">({user?.role})</span>
            </span>
            <button onClick={logout} className="rounded-md border border-slate-300 px-3 py-1 text-slate-600 hover:bg-slate-100">
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
