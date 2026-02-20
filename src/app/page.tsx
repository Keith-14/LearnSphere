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
          <Image src="/pingo_logo.png" alt="Learning Sphere" width={160} height={160} className="mx-auto mb-4 rounded-3xl" />
          <h1 className="text-4xl font-black text-[#3C3C3C]">Learning Sphere</h1>
          <p className="text-[#AFAFAF] font-bold mt-1 text-lg">Your emotion-aware study companion 🚀</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-3xl border-2 border-[#E5E5E5] border-b-8 p-10 shadow-xl">
          <h2 className="text-2xl font-extrabold text-[#3C3C3C] text-center mb-6">Welcome back! 👋</h2>

          <form onSubmit={(e) => {
            e.preventDefault();
            // Extract name from email (e.g. rishi@example.com -> Rishi)
            const extractedName = email.split("@")[0].charAt(0).toUpperCase() + email.split("@")[0].slice(1);
            localStorage.setItem("userName", extractedName);
            localStorage.setItem("userRole", role);
            router.push(`/${role}`);
          }}>
            {/* Role Switcher with Icons */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <button
                type="button"
                onClick={() => setRole("student")}
                className={`flex flex-col items-center gap-2 p-6 rounded-2xl border-2 border-b-6 transition-all duration-100 ${role === "student"
                  ? "border-[#1CB0F6] bg-[#DDF4FF]"
                  : "border-[#E5E5E5] bg-white hover:bg-[#F7F7F7]"
                  }`}
              >
                <Image src="/pingo_student.png" alt="Student" width={64} height={64} className="rounded-xl" />
                <span className={`text-xs font-black uppercase tracking-widest ${role === "student" ? "text-[#1CB0F6]" : "text-[#AFAFAF]"}`}>
                  🎓 Student
                </span>
              </button>
              <button
                type="button"
                onClick={() => setRole("teacher")}
                className={`flex flex-col items-center gap-2 p-6 rounded-2xl border-2 border-b-6 transition-all duration-100 ${role === "teacher"
                  ? "border-[#1CB0F6] bg-[#DDF4FF]"
                  : "border-[#E5E5E5] bg-white hover:bg-[#F7F7F7]"
                  }`}
              >
                <Image src="/pingo_teacher.png" alt="Teacher" width={64} height={64} className="rounded-xl" />
                <span className={`text-xs font-black uppercase tracking-widest ${role === "teacher" ? "text-[#1CB0F6]" : "text-[#AFAFAF]"}`}>
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
                required
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="mt-1.5 w-full rounded-2xl border-2 border-[#E5E5E5] bg-white px-5 py-4 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#1CB0F6] transition-colors"
              />
            </div>

            {/* Password */}
            <div className="mb-8">
              <label className="text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Password</label>
              <input
                type="password"
                value={password}
                required
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1.5 w-full rounded-2xl border-2 border-[#E5E5E5] bg-white px-5 py-4 text-sm font-bold text-[#3C3C3C] placeholder:text-[#DEDEDE] focus:outline-none focus:border-[#1CB0F6] transition-colors"
              />
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full py-4 rounded-xl bg-[#1CB0F6] border-b-6 border-[#0D8ECF] text-white text-base font-black uppercase tracking-widest transition-all hover:bg-[#18A0E0] active:border-b-0 active:mt-1 shadow-lg shadow-[#1CB0F6]/20"
            >
              {role === "student" ? "Start Learning →" : "Open Dashboard →"}
            </button>
          </form>

          <p className="text-center text-xs font-bold text-[#AFAFAF] mt-6">
            Don&apos;t have an account?{" "}
            <span className="text-[#1CB0F6] cursor-pointer hover:underline">Sign up free!</span>
          </p>
        </div>
      </div>
    </div>
  );
}
