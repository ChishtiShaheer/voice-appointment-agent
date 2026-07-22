const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export type ChatResponse = {
  session_id: string;
  reply: string;
  state: string;
};

export async function sendMessage(sessionId: string | null, message: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

export type Appointment = {
  id: string;
  full_name: string;
  phone_number: string;
  appointment_type: string;
  appointment_date: string;
  appointment_time: string;
  reason: string;
  status: string;
};

export async function fetchAppointments(): Promise<Appointment[]> {
  const res = await fetch(`${API_BASE}/appointments`);
  if (!res.ok) throw new Error("Failed to load appointments");
  return res.json();
}
