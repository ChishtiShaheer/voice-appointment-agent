"use client";

import { useState } from "react";
import Link from "next/link";
import VoiceRecorder, { speak } from "@/components/VoiceRecorder";
import { sendMessage } from "@/lib/api";

type Turn = { role: "agent" | "user"; text: string };

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([
    { role: "agent", text: "Hi — I can help you book, reschedule, or cancel an appointment. What would you like to do?" },
  ]);
  const [busy, setBusy] = useState(false);

  const handleUserText = async (text: string) => {
    setTurns((t) => [...t, { role: "user", text }]);
    setBusy(true);
    try {
      const res = await sendMessage(sessionId, text);
      setSessionId(res.session_id);
      setTurns((t) => [...t, { role: "agent", text: res.reply }]);
      speak(res.reply);
    } catch {
      setTurns((t) => [...t, { role: "agent", text: "Something went wrong reaching the server." }]);
    } finally {
      setBusy(false);
    }
  };

  const [typed, setTyped] = useState("");

  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-10">
      <div className="w-full max-w-xl">
        <div className="flex items-baseline justify-between mb-8">
          <h1 className="font-display text-3xl text-ink">Appointment Desk</h1>
          <Link href="/dashboard" className="text-sm text-slate underline underline-offset-4 hover:text-accent">
            Manage appointments
          </Link>
        </div>

        <div className="bg-white border border-line rounded-2xl p-6 min-h-[420px] flex flex-col gap-3 mb-6">
          {turns.map((turn, i) => (
            <div
              key={i}
              className={`max-w-[80%] px-4 py-2 rounded-xl text-sm leading-relaxed ${
                turn.role === "agent"
                  ? "bg-mist text-ink self-start"
                  : "bg-ink text-white self-end"
              }`}
            >
              {turn.text}
            </div>
          ))}
          {busy && <div className="text-xs text-slate self-start">thinking…</div>}
        </div>

        <div className="flex items-center gap-4 justify-center">
          <VoiceRecorder onResult={handleUserText} disabled={busy} />
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!typed.trim()) return;
              handleUserText(typed.trim());
              setTyped("");
            }}
            className="flex-1 flex gap-2"
          >
            <input
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              placeholder="Or type your reply…"
              className="flex-1 border border-line rounded-full px-4 py-2 text-sm outline-none focus:border-accent"
            />
            <button
              type="submit"
              disabled={busy}
              className="px-4 py-2 rounded-full bg-ink text-white text-sm disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
