"use client";

import React from "react";
import Image from "next/image";
import { StudentProfile, examOptions, pingoAvatars } from "@/lib/mockData";

interface SidebarProps {
    profile: StudentProfile;
    activeNav: string;
    onNavChange: (nav: string) => void;
    selectedExam: string;
    onExamChange: (exam: string) => void;
    role?: "student" | "teacher";
}

const studentNavItems = [
    { key: "dashboard", label: "Dashboard", icon: "🏠" },
    { key: "session", label: "Study Session", icon: "📖" },
    { key: "quiz", label: "Start Quiz", icon: "🧩" },
    { key: "spark", label: "Motivation Spark", icon: "🎡" },
    { key: "progress", label: "Progress", icon: "🏆" },
];

const teacherNavItems = [
    { key: "dashboard", label: "Dashboard", icon: "🏠" },
    { key: "students", label: "Students", icon: "👥" },
    { key: "video", label: "Video Analysis", icon: "🎥" },
    { key: "analytics", label: "Analytics", icon: "📊" },
    { key: "reports", label: "Reports", icon: "📋" },
];

export default function Sidebar({
    profile,
    activeNav,
    onNavChange,
    selectedExam,
    onExamChange,
    role = "student",
}: SidebarProps) {
    const navItems = role === "student" ? studentNavItems : teacherNavItems;
    const roleIcon = role === "student" ? "/pingo_student.png" : "/pingo_teacher.png";

    return (
        <aside className="w-[260px] min-h-screen bg-white border-r-2 border-[#E5E5E5] flex flex-col fixed left-0 top-0 z-30">
            {/* Logo */}
            <div className="p-5 border-b-2 border-[#E5E5E5]">
                <div className="flex items-center gap-2.5">
                    <Image src="/pingo_logo.png" alt="Learning Sphere" width={40} height={40} className="rounded-xl" />
                    <span className="text-xl font-extrabold text-[#3C3C3C]">Learning Sphere</span>
                </div>
            </div>

            {/* Profile Card */}
            <div className="p-5 border-b-2 border-[#E5E5E5]">
                <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-full overflow-hidden border-2 border-[#E5E5E5] bg-[#F7F7F7] flex-shrink-0">
                        <Image src={roleIcon} alt={role} width={44} height={44} className="object-cover" />
                    </div>
                    <div>
                        <p className="text-sm font-extrabold text-[#3C3C3C]">{profile.name}</p>
                        <p className="text-xs font-bold text-[#AFAFAF]">{profile.email}</p>
                    </div>
                </div>
            </div>

            {/* Exam Dropdown */}
            <div className="px-5 py-4 border-b-2 border-[#E5E5E5]">
                <label className="text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Exam</label>
                <select
                    value={selectedExam}
                    onChange={(e) => onExamChange(e.target.value)}
                    className="mt-1.5 w-full rounded-xl border-2 border-[#E5E5E5] bg-white px-3 py-2 text-sm font-bold text-[#3C3C3C] focus:outline-none focus:border-[#1CB0F6] transition-colors"
                >
                    {examOptions.map((exam) => (
                        <option key={exam} value={exam}>{exam}</option>
                    ))}
                </select>
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 px-3 py-4">
                {navItems.map((item) => (
                    <button
                        key={item.key}
                        onClick={() => onNavChange(item.key)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-extrabold transition-all duration-100 mb-1
              ${activeNav === item.key
                                ? "bg-[#DDF4FF] text-[#1CB0F6] border-2 border-[#1CB0F6]"
                                : "text-[#3C3C3C] hover:bg-[#F7F7F7] border-2 border-transparent"
                            }`}
                    >
                        <span className="text-lg">{item.icon}</span>
                        {item.label}
                    </button>
                ))}
            </nav>

            {/* Streak Card */}
            {role === "student" && (
                <div className="mx-4 mb-5 p-4 rounded-2xl bg-[#FFF3CD] border-2 border-[#FFC800] border-b-4">
                    <div className="flex items-center gap-2.5">
                        <span className="text-2xl">🔥</span>
                        <div>
                            <p className="text-sm font-extrabold text-[#FF9600]">{profile.streak}-day streak!</p>
                            <p className="text-xs font-bold text-[#AFAFAF]">Keep it going!</p>
                        </div>
                    </div>
                </div>
            )}
        </aside>
    );
}
