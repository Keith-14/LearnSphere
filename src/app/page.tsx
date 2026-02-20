"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"student" | "teacher">("student");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(`/${role}`);
  };

  return (
    <div className="min-h-screen bg-[#F7F7F7] flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-[#58CC02] flex items-center justify-center mx-auto mb-4 border-b-4 border-[#46A302] shadow-lg">
            <span className="text-white text-2xl font-black">LS</span>
          </div>
          <h1 className="text-3xl font-black text-[#3C3C3C]">Learning Sphere</h1>
          <p className="text-[#AFAFAF] font-bold mt-1">Your emotion-aware study companion 🚀</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 p-8">
          <h2 className="text-xl font-extrabold text-[#3C3C3C] text-center mb-6">Welcome back! 👋</h2>

          <form onSubmit={handleLogin}>
            {/* Role Switcher */}
            <div className="flex rounded-xl border-2 border-[#E5E5E5] overflow-hidden mb-6">
              <button
                type="button"
                onClick={() => setRole("student")}
                className={`flex-1 py-3 text-sm font-extrabold uppercase tracking-wide transition-colors ${role === "student"
                    ? "bg-[#58CC02] text-white"
                    : "bg-white text-[#AFAFAF] hover:bg-[#F7F7F7]"
                  }`}
              >
                🎓 Student
              </button>
              <button
                type="button"
                onClick={() => setRole("teacher")}
                className={`flex-1 py-3 text-sm font-extrabold uppercase tracking-wide transition-colors ${role === "teacher"
                    ? "bg-[#1CB0F6] text-white"
                    : "bg-white text-[#AFAFAF] hover:bg-[#F7F7F7]"
                  }`}
              >
                📚 Teacher
              </button>
            </div>

            {/* Email */}
            <div className="mb-4">
              <label className="text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1.5 w-full rounded-xl border-2 border-[#E5E5E5] bg-white px-4 py-3 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#58CC02] transition-colors"
              />
            </div>

            {/* Password */}
            <div className="mb-6">
              <label className="text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1.5 w-full rounded-xl border-2 border-[#E5E5E5] bg-white px-4 py-3 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#58CC02] transition-colors"
              />
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className={`w-full py-3.5 rounded-xl text-white text-sm font-extrabold uppercase tracking-wide transition-all border-b-4 active:border-b-0 active:mt-1 ${role === "student"
                  ? "bg-[#58CC02] border-[#46A302] hover:bg-[#4DB802]"
                  : "bg-[#1CB0F6] border-[#0D8ECF] hover:bg-[#18A0E0]"
                }`}
            >
              {role === "student" ? "🎓 Start Learning" : "📚 Open Dashboard"}
            </button>
          </form>

          <p className="text-center text-xs font-bold text-[#AFAFAF] mt-5">
            Don&apos;t have an account?{" "}
            <span className="text-[#1CB0F6] cursor-pointer hover:underline">Sign up free!</span>
          </p>
        </div>

        <p className="text-center text-xs font-bold text-[#DEDEDE] mt-6">
          Made with 💚 by Learning Sphere
        </p>
      </div>
    </div>
  );
}
