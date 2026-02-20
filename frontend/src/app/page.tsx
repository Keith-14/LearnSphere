"use client";

import React, { useState } from "react";
import Image from "next/image";
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
          <Image src="/pingo_logo.png" alt="Learning Sphere" width={80} height={80} className="mx-auto mb-4 rounded-2xl" />
          <h1 className="text-3xl font-black text-[#3C3C3C]">Learning Sphere</h1>
          <p className="text-[#AFAFAF] font-bold mt-1">Your emotion-aware study companion 🚀</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 p-8">
          <h2 className="text-xl font-extrabold text-[#3C3C3C] text-center mb-6">Welcome back! 👋</h2>

          <form onSubmit={handleLogin}>
            {/* Role Switcher with Icons */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <button
                type="button"
                onClick={() => setRole("student")}
                className={`flex flex-col items-center gap-2 p-4 rounded-2xl border-2 border-b-4 transition-all duration-100 ${role === "student"
                  ? "border-[#1CB0F6] bg-[#DDF4FF]"
                  : "border-[#E5E5E5] bg-white hover:bg-[#F7F7F7]"
                  }`}
              >
                <Image src="/pingo_student.png" alt="Student" width={56} height={56} className="rounded-xl" />
                <span className={`text-sm font-extrabold uppercase tracking-wide ${role === "student" ? "text-[#1CB0F6]" : "text-[#AFAFAF]"}`}>
                  🎓 Student
                </span>
              </button>
              <button
                type="button"
                onClick={() => setRole("teacher")}
                className={`flex flex-col items-center gap-2 p-4 rounded-2xl border-2 border-b-4 transition-all duration-100 ${role === "teacher"
                  ? "border-[#1CB0F6] bg-[#DDF4FF]"
                  : "border-[#E5E5E5] bg-white hover:bg-[#F7F7F7]"
                  }`}
              >
                <Image src="/pingo_teacher.png" alt="Teacher" width={56} height={56} className="rounded-xl" />
                <span className={`text-sm font-extrabold uppercase tracking-wide ${role === "teacher" ? "text-[#1CB0F6]" : "text-[#AFAFAF]"}`}>
                  📚 Teacher
                </span>
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
                className="mt-1.5 w-full rounded-xl border-2 border-[#E5E5E5] bg-white px-4 py-3 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#1CB0F6] transition-colors"
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
                className="mt-1.5 w-full rounded-xl border-2 border-[#E5E5E5] bg-white px-4 py-3 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#1CB0F6] transition-colors"
              />
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full py-3.5 rounded-xl bg-[#1CB0F6] border-b-4 border-[#0D8ECF] text-white text-sm font-extrabold uppercase tracking-wide transition-all hover:bg-[#18A0E0] active:border-b-0 active:mt-1"
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
