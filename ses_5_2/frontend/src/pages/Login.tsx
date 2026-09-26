import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = [
  { role: "admin", email: "admin@carta.health", password: "AdminPass123!" },
  { role: "clinician", email: "clinician@carta.health", password: "ClinicianPass123!" },
  { role: "analyst", email: "analyst@carta.health", password: "AnalystPass123!" },
];

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("clinician@carta.health");
  const [password, setPassword] = useState("ClinicianPass123!");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-bold text-carta-700">Carta Healthcare</h1>
        <p className="mt-1 text-sm text-slate-500">Clinical data extraction platform</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-carta-500 focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-carta-500 focus:outline-none"
              required
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-carta-600 px-3 py-2 text-sm font-medium text-white hover:bg-carta-700 disabled:opacity-50"
          >
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-6 border-t border-slate-100 pt-4">
          <p className="text-xs font-medium text-slate-500">Demo accounts (seeded on startup)</p>
          <ul className="mt-2 space-y-1 text-xs text-slate-500">
            {DEMO_ACCOUNTS.map((acc) => (
              <li key={acc.role}>
                <button
                  type="button"
                  className="text-carta-600 hover:underline"
                  onClick={() => {
                    setEmail(acc.email);
                    setPassword(acc.password);
                  }}
                >
                  {acc.role}
                </button>{" "}
                &mdash; {acc.email}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
