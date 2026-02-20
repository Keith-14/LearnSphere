"use client";

import React, { useState } from "react";
import Image from "next/image";
import Sidebar from "@/components/Sidebar";
import MetricsCard from "@/components/MetricsCard";
import DashboardCard from "@/components/DashboardCard";
import EmotionBadge from "@/components/EmotionBadge";
import StudentTable from "@/components/StudentTable";
import VideoAnalysis from "@/components/VideoAnalysis";
import {
    mockStudentProfile,
    mockTeacherMetrics,
    mockStudents,
    pingoAvatars,
} from "@/lib/mockData";

const metricColors = ["#1CB0F6", "#FF4B4B", "#CE82FF", "#58CC02"];

export default function TeacherPage() {
    const [activeNav, setActiveNav] = useState("dashboard");
    const [selectedExam, setSelectedExam] = useState("GRE");

    return (
        <div className="flex min-h-screen bg-[#F7F7F7]">
            <Sidebar
                profile={{ ...mockStudentProfile, name: "Dr. Ananya Roy", initials: "AR", email: "ananya@learningsphere.io" }}
                activeNav={activeNav}
                onNavChange={setActiveNav}
                selectedExam={selectedExam}
                onExamChange={setSelectedExam}
                role="teacher"
            />

            <main className="ml-[260px] flex-1 p-8">

                {/* ─── DASHBOARD ─── */}
                {activeNav === "dashboard" && (
                    <>
                        <div className="mb-8 flex items-center gap-4">
                            <Image src={pingoAvatars["Focused"]} alt="Pingo" width={56} height={56} className="rounded-full border-2 border-[#1CB0F6]" />
                            <div>
                                <h1 className="text-3xl font-black text-[#3C3C3C]">📊 Emotional Analytics Overview</h1>
                                <p className="text-[#AFAFAF] font-bold mt-0.5">Monitor how your students are feeling and performing!</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
                            {mockTeacherMetrics.map((metric, i) => (
                                <MetricsCard key={metric.label} label={metric.label} value={metric.value} subtext={metric.subtext} icon={metric.icon} color={metricColors[i]} />
                            ))}
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">🎭 Emotion Distribution</h3>
                                <div className="h-48 flex items-center justify-center rounded-xl bg-[#F7F7F7] border-2 border-dashed border-[#E5E5E5]">
                                    <div className="text-center">
                                        <Image src={pingoAvatars["Calm"]} alt="Chart" width={48} height={48} className="mx-auto mb-2" />
                                        <p className="text-[#AFAFAF] text-sm font-bold">Chart coming soon!</p>
                                    </div>
                                </div>
                            </DashboardCard>
                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">📈 Weekly Emotional Trend</h3>
                                <div className="h-48 flex items-center justify-center rounded-xl bg-[#F7F7F7] border-2 border-dashed border-[#E5E5E5]">
                                    <div className="text-center">
                                        <Image src={pingoAvatars["Focused"]} alt="Chart" width={48} height={48} className="mx-auto mb-2" />
                                        <p className="text-[#AFAFAF] text-sm font-bold">Chart coming soon!</p>
                                    </div>
                                </div>
                            </DashboardCard>
                        </div>

                        <StudentTable students={mockStudents} />
                    </>
                )}

                {/* ─── STUDENTS ─── */}
                {activeNav === "students" && (
                    <>
                        <div className="mb-8 flex items-center gap-3">
                            <Image src={pingoAvatars["Calm"]} alt="Pingo" width={40} height={40} className="rounded-full border-2 border-[#58CC02]" />
                            <div>
                                <h1 className="text-3xl font-black text-[#3C3C3C]">👥 Students</h1>
                                <p className="text-[#AFAFAF] font-bold mt-0.5">View and manage all enrolled students</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-6">
                            <DashboardCard className="text-center">
                                <Image src={pingoAvatars["Calm"]} alt="Total" width={40} height={40} className="mx-auto mb-2" />
                                <p className="text-3xl font-black text-[#1CB0F6]">{mockStudents.length}</p>
                                <p className="text-sm font-bold text-[#AFAFAF]">Total Students</p>
                            </DashboardCard>
                            <DashboardCard className="text-center">
                                <Image src={pingoAvatars["Stressed"]} alt="High Risk" width={40} height={40} className="mx-auto mb-2" />
                                <p className="text-3xl font-black text-[#FF4B4B]">{mockStudents.filter(s => s.riskLevel === "High").length}</p>
                                <p className="text-sm font-bold text-[#AFAFAF]">High Risk</p>
                            </DashboardCard>
                            <DashboardCard className="text-center">
                                <Image src={pingoAvatars["Focused"]} alt="Low Risk" width={40} height={40} className="mx-auto mb-2" />
                                <p className="text-3xl font-black text-[#58CC02]">{mockStudents.filter(s => s.riskLevel === "Low").length}</p>
                                <p className="text-sm font-bold text-[#AFAFAF]">Low Risk</p>
                            </DashboardCard>
                        </div>

                        <StudentTable students={mockStudents} />
                    </>
                )}

                {/* ─── VIDEO ANALYSIS ─── */}
                {activeNav === "video" && (
                    <>
                        <div className="mb-8 flex items-center gap-3">
                            <Image src={pingoAvatars["Confused"]} alt="Pingo" width={40} height={40} className="rounded-full border-2 border-[#CE82FF]" />
                            <div>
                                <h1 className="text-3xl font-black text-[#3C3C3C]">🎥 Video Analysis</h1>
                                <p className="text-[#AFAFAF] font-bold mt-0.5">Monitor student emotions via video feed analysis</p>
                            </div>
                        </div>
                        <VideoAnalysis />
                    </>
                )}

                {/* ─── ANALYTICS ─── */}
                {activeNav === "analytics" && (
                    <>
                        <div className="mb-8 flex items-center gap-3">
                            <Image src={pingoAvatars["Focused"]} alt="Pingo" width={40} height={40} className="rounded-full border-2 border-[#1CB0F6]" />
                            <div>
                                <h1 className="text-3xl font-black text-[#3C3C3C]">📊 Analytics</h1>
                                <p className="text-[#AFAFAF] font-bold mt-0.5">Deep dive into student emotional and performance data</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">🎭 Emotion Distribution</h3>
                                <div className="space-y-3">
                                    {(["Stressed", "Focused", "Confused", "Calm"] as const).map((emotion) => {
                                        const count = mockStudents.filter(s => s.emotion === emotion).length;
                                        const pct = Math.round((count / mockStudents.length) * 100);
                                        const colors: Record<string, string> = { Stressed: "#FF4B4B", Focused: "#1CB0F6", Confused: "#CE82FF", Calm: "#58CC02" };
                                        return (
                                            <div key={emotion} className="flex items-center gap-3">
                                                <Image src={pingoAvatars[emotion]} alt={emotion} width={28} height={28} className="rounded-full" />
                                                <EmotionBadge emotion={emotion} showAvatar={false} />
                                                <div className="flex-1 h-4 rounded-full bg-[#E5E5E5] overflow-hidden">
                                                    <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: colors[emotion] }} />
                                                </div>
                                                <span className="font-extrabold text-sm text-[#3C3C3C] min-w-[50px] text-right">{count} ({pct}%)</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </DashboardCard>

                            <DashboardCard>
                                <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">⚠️ Risk Level Breakdown</h3>
                                <div className="space-y-3">
                                    {(["High", "Medium", "Low"] as const).map((risk) => {
                                        const count = mockStudents.filter(s => s.riskLevel === risk).length;
                                        const pct = Math.round((count / mockStudents.length) * 100);
                                        const colors: Record<string, string> = { High: "#FF4B4B", Medium: "#FFC800", Low: "#58CC02" };
                                        const emojis: Record<string, string> = { High: "🔴", Medium: "🟡", Low: "🟢" };
                                        return (
                                            <div key={risk} className="flex items-center gap-3 p-3 rounded-xl bg-[#F7F7F7] border-2 border-[#E5E5E5]">
                                                <span className="text-xl">{emojis[risk]}</span>
                                                <span className="font-extrabold text-[#3C3C3C] min-w-[70px]">{risk}</span>
                                                <div className="flex-1 h-4 rounded-full bg-[#E5E5E5] overflow-hidden">
                                                    <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: colors[risk] }} />
                                                </div>
                                                <span className="font-extrabold text-sm text-[#3C3C3C]">{count}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </DashboardCard>
                        </div>

                        <DashboardCard>
                            <h3 className="text-lg font-extrabold text-[#3C3C3C] mb-4">📈 Weekly Emotional Trend</h3>
                            <div className="h-48 flex items-center justify-center rounded-xl bg-[#F7F7F7] border-2 border-dashed border-[#E5E5E5]">
                                <div className="text-center">
                                    <Image src={pingoAvatars["Calm"]} alt="Trend" width={48} height={48} className="mx-auto mb-2" />
                                    <p className="text-[#AFAFAF] text-sm font-bold">Trend chart coming soon!</p>
                                </div>
                            </div>
                        </DashboardCard>
                    </>
                )}

                {/* ─── REPORTS ─── */}
                {activeNav === "reports" && (
                    <>
                        <div className="mb-8 flex items-center gap-3">
                            <Image src={pingoAvatars["Calm"]} alt="Pingo" width={40} height={40} className="rounded-full border-2 border-[#58CC02]" />
                            <div>
                                <h1 className="text-3xl font-black text-[#3C3C3C]">📋 Reports</h1>
                                <p className="text-[#AFAFAF] font-bold mt-0.5">Generate and review student performance reports</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-6">
                            {[
                                { title: "Weekly Summary", desc: "Overview of student emotions and performance this week", emoji: "📅", color: "#1CB0F6", avatar: "Focused" as const },
                                { title: "Risk Assessment", desc: "Identify students who may need additional support", emoji: "⚠️", color: "#FF4B4B", avatar: "Stressed" as const },
                                { title: "Emotion Patterns", desc: "Analyze emotional trends across all sessions", emoji: "🎭", color: "#CE82FF", avatar: "Confused" as const },
                                { title: "Engagement Report", desc: "Track student participation and activity levels", emoji: "📊", color: "#58CC02", avatar: "Calm" as const },
                            ].map((report) => (
                                <DashboardCard key={report.title} className="cursor-pointer group hover:border-b-2 hover:mt-[2px] transition-all duration-100">
                                    <div className="flex items-start gap-4">
                                        <Image src={pingoAvatars[report.avatar]} alt={report.title} width={56} height={56} className="rounded-2xl border-2 border-[#E5E5E5]" />
                                        <div className="flex-1">
                                            <h3 className="text-base font-extrabold text-[#3C3C3C] group-hover:text-[#1CB0F6] transition-colors">{report.title}</h3>
                                            <p className="text-sm font-bold text-[#AFAFAF] mt-1">{report.desc}</p>
                                            <button className="mt-3 text-xs font-extrabold uppercase tracking-wide px-4 py-2 rounded-xl border-b-4 text-white transition-all active:border-b-0 active:mt-[3px]" style={{ backgroundColor: report.color, borderColor: `${report.color}CC` }}>
                                                Generate Report
                                            </button>
                                        </div>
                                    </div>
                                </DashboardCard>
                            ))}
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
