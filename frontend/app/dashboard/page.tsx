"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchAppointments, Appointment } from "@/lib/api";

export default function Dashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAppointments()
      .then(setAppointments)
      .finally(() => setLoading(false));
  }, []);

  const visible =
    filter === "all" ? appointments : appointments.filter((a) => a.status === filter);

  return (
    <main className="min-h-screen px-4 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-baseline justify-between mb-8">
          <h1 className="font-display text-3xl text-ink">Appointments</h1>
          <Link href="/" className="text-sm text-slate underline underline-offset-4 hover:text-accent">
            Back to booking
          </Link>
        </div>

        <div className="flex gap-2 mb-4">
          {["all", "booked", "rescheduled", "cancelled"].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded-full text-xs border ${
                filter === s ? "bg-ink text-white border-ink" : "border-line text-slate"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="bg-white border border-line rounded-2xl overflow-hidden">
          {loading ? (
            <div className="p-6 text-sm text-slate">Loading…</div>
          ) : visible.length === 0 ? (
            <div className="p-6 text-sm text-slate">No appointments yet.</div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-mist text-left text-slate">
                  <th className="p-3 font-medium">Name</th>
                  <th className="p-3 font-medium">Type</th>
                  <th className="p-3 font-medium">Date</th>
                  <th className="p-3 font-medium">Time</th>
                  <th className="p-3 font-medium">Phone</th>
                  <th className="p-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((a) => (
                  <tr key={a.id} className="border-t border-line">
                    <td className="p-3">{a.full_name}</td>
                    <td className="p-3">{a.appointment_type}</td>
                    <td className="p-3">{a.appointment_date}</td>
                    <td className="p-3">{a.appointment_time}</td>
                    <td className="p-3">{a.phone_number}</td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs ${
                          a.status === "booked"
                            ? "bg-accent/10 text-accent"
                            : a.status === "cancelled"
                            ? "bg-red-100 text-red-700"
                            : "bg-mist text-slate"
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </main>
  );
}
