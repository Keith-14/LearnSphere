"use client";

import React, { useState } from "react";
import Sidebar from "@/components/Sidebar";
import MetricsCard from "@/components/MetricsCard";
import DashboardCard from "@/components/DashboardCard";
import EmotionBadge from "@/components/EmotionBadge";
import ChatWindow from "@/components/ChatWindow";
import {
    mockStudentProfile,
    mockStudentMetrics,
    mockRecentSessions,
} from "@/lib/mockData";

const metricColors = ["#58CC02", "#FF9600", "#FF4B4B", "#1CB0F6"];

export default function StudentPage() {
    const [activeNav, setActiveNav] = useState("dashboard");
    const [selectedExam, setSelectedExam] = useState(mockStudentProfile.exam);
    const [sessionActive, setSessionActive] = useState(false);

    const handleNavChange = (nav: string) => {
        setActiveNav(nav);
        if (nav !== "session") setSessionActive(false);
        if (nav === "session") setSessionActive(true);
    };

    return (
        <div className="flex min-h-screen bg-[#F7F7F7]">
            <Sidebar
                profile={mockStudentProfile}
                activeNav={activeNav}
                onNavChange={handleNavChange}
                selectedExam={selectedExam}
                onExamChange={setSelectedExam}
                role="student"
            />

            <main className="ml-[260px] flex-1 p-8">

                {/* ─── DASHBOARD ─── */}
                {activeNav === "dashboard" && !sessionActive && (
                    <>
                        <div className="mb-8">
                            <h1 className="text-3xl font-black text-[#3C3C3C]">
                                Hey, {mockStudentProfile.name.split(" ")[0]}! 👋
                            </h1>
                            <p className="text-[#AFAFAF] font-bold mt-1">Keep up your amazing streak! You&apos;re doing great! 🚀</p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
                            {mockStudentMetrics.map((metric, i) => (
                                <MetricsCard
                                    key={metric.label}
                                    label={metric.label}
                                    value={metric.value}
                                    subtext={metric.subtext}
                                    icon={metric.icon}
                                    color={metricColors[i]}
                                />
                            ))}
                        </div>

                        <DashboardCard className="mb-6 cursor-pointer group hover:border-b-2 hover:mt-[2px] transition-all duration-100">
                            <button
                                onClick={() => { setSessionActive(true); setActiveNav("session"); }}
                                className="w-full text-left"
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-xl font-extrabold text-[#3C3C3C] group-hover:text-[#58CC02] transition-colors">
                                            📖 Start Study Session
                                        </h2>
                                        <p className="text-sm font-bold text-[#AFAFAF] mt-1">
                                            Jump into an adaptive session tailored just for you!
                                        </p>
                                    </div>
                                    <div className="w-14 h-14 rounded-2xl bg-[#58CC02] flex items-center justify-center border-b-4 border-[#46A302] group-hover:border-b-2 group-hover:mt-[2px] transition-all">
                                        <span className="text-white text-2xl font-black">→</span>
                                    </div>
                                </div>
                            </button>
                        </DashboardCard>

                        <DashboardCard>
                            <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">📝 Recent Sessions</h3>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b-2 border-[#E5E5E5]">
                                            <th className="pb-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Topic</th>
                                            <th className="pb-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Date</th>
                                            <th className="pb-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Duration</th>
                                            <th className="pb-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Emotion</th>
                                            <th className="pb-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Score</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y-2 divide-[#E5E5E5]">
                                        {mockRecentSessions.map((session) => (
                                            <tr key={session.id} className="hover:bg-[#F7F7F7] transition-colors">
                                                <td className="py-3.5 font-extrabold text-[#3C3C3C]">{session.topic}</td>
                                                <td className="py-3.5 font-bold text-[#AFAFAF]">{session.date}</td>
                                                <td className="py-3.5 font-bold text-[#AFAFAF]">{session.duration}</td>
                                                <td className="py-3.5"><EmotionBadge emotion={session.emotion} /></td>
                                                <td className="py-3.5">
                                                    <span className={`font-extrabold text-base ${session.score >= 75 ? "text-[#58CC02]" : session.score >= 60 ? "text-[#FFC800]" : "text-[#FF4B4B]"}`}>
                                                        {session.score}%
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </DashboardCard>
                    </>
                )}

                {/* ─── STUDY SESSION ─── */}
                {(activeNav === "session" || sessionActive) && (
                    <div>
                        <div className="mb-6">
                            <h1 className="text-3xl font-black text-[#3C3C3C]">📖 Study Session</h1>
                            <p className="text-[#AFAFAF] font-bold mt-1">Your adaptive learning session is live!</p>
                        </div>
                        <ChatWindow onClose={() => { setSessionActive(false); setActiveNav("dashboard"); }} />
                    </div>
                )}

                {/* ─── EMOTION INSIGHTS ─── */}
                {activeNav === "insights" && !sessionActive && (
                    <>
                        <div className="mb-8">
                            <h1 className="text-3xl font-black text-[#3C3C3C]">💡 Emotion Insights</h1>
                            <p className="text-[#AFAFAF] font-bold mt-1">Understand your emotional patterns across study sessions</p>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">🎭 Emotion Over Time</h3>
                                <div className="h-48 flex items-center justify-center rounded-xl bg-[#F7F7F7] border-2 border-dashed border-[#E5E5E5]">
                                    <div className="text-center">
                                        <p className="text-3xl mb-2">📈</p>
                                        <p className="text-[#AFAFAF] text-sm font-bold">Chart coming soon!</p>
                                    </div>
                                </div>
                            </DashboardCard>
                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">🧠 Emotion Breakdown</h3>
                                <div className="h-48 flex items-center justify-center rounded-xl bg-[#F7F7F7] border-2 border-dashed border-[#E5E5E5]">
                                    <div className="text-center">
                                        <p className="text-3xl mb-2">🥧</p>
                                        <p className="text-[#AFAFAF] text-sm font-bold">Chart coming soon!</p>
                                    </div>
                                </div>
                            </DashboardCard>
                        </div>

                        <DashboardCard>
                            <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">📋 Session Emotion Log</h3>
                            <div className="space-y-3">
                                {mockRecentSessions.map((s) => (
                                    <div key={s.id} className="flex items-center justify-between p-4 rounded-xl bg-[#F7F7F7] border-2 border-[#E5E5E5]">
                                        <div>
                                            <p className="font-extrabold text-[#3C3C3C]">{s.topic}</p>
                                            <p className="text-xs font-bold text-[#AFAFAF]">{s.date} · {s.duration}</p>
                                        </div>
                                        <EmotionBadge emotion={s.emotion} />
                                    </div>
                                ))}
                            </div>
                        </DashboardCard>
                    </>
                )}

                {/* ─── PROGRESS ─── */}
                {activeNav === "progress" && !sessionActive && (
                    <>
                        <div className="mb-8">
                            <h1 className="text-3xl font-black text-[#3C3C3C]">🏆 Progress</h1>
                            <p className="text-[#AFAFAF] font-bold mt-1">Track your learning journey and achievements!</p>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-6">
                            <DashboardCard className="text-center">
                                <p className="text-4xl mb-2">🔥</p>
                                <p className="text-3xl font-black text-[#FF9600]">{mockStudentProfile.streak}</p>
                                <p className="text-sm font-bold text-[#AFAFAF]">Day Streak</p>
                            </DashboardCard>
                            <DashboardCard className="text-center">
                                <p className="text-4xl mb-2">📚</p>
                                <p className="text-3xl font-black text-[#1CB0F6]">{mockRecentSessions.length}</p>
                                <p className="text-sm font-bold text-[#AFAFAF]">Sessions Completed</p>
                            </DashboardCard>
                            <DashboardCard className="text-center">
                                <p className="text-4xl mb-2">⭐</p>
                                <p className="text-3xl font-black text-[#FFC800]">
                                    {Math.round(mockRecentSessions.reduce((a, s) => a + s.score, 0) / mockRecentSessions.length)}%
                                </p>
                                <p className="text-sm font-bold text-[#AFAFAF]">Avg Score</p>
                            </DashboardCard>
                        </div>

                        <DashboardCard>
                            <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">📊 Score History</h3>
                            <div className="space-y-3">
                                {mockRecentSessions.map((s) => (
                                    <div key={s.id} className="flex items-center gap-4 p-4 rounded-xl bg-[#F7F7F7] border-2 border-[#E5E5E5]">
                                        <div className="flex-1">
                                            <p className="font-extrabold text-[#3C3C3C]">{s.topic}</p>
                                            <p className="text-xs font-bold text-[#AFAFAF]">{s.date}</p>
                                        </div>
                                        <div className="w-32 h-3 rounded-full bg-[#E5E5E5] overflow-hidden">
                                            <div
                                                className="h-full rounded-full transition-all"
                                                style={{
                                                    width: `${s.score}%`,
                                                    backgroundColor: s.score >= 75 ? "#58CC02" : s.score >= 60 ? "#FFC800" : "#FF4B4B",
                                                }}
                                            />
                                        </div>
                                        <span className={`font-extrabold text-sm min-w-[40px] text-right ${s.score >= 75 ? "text-[#58CC02]" : s.score >= 60 ? "text-[#FFC800]" : "text-[#FF4B4B]"}`}>
                                            {s.score}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </DashboardCard>
                    </>
                )}
            </main>
        </div>
    );
}
