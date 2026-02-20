"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import EmotionBadge from "./EmotionBadge";
import { mockStudents, pingoAvatars } from "@/lib/mockData";
import type { Emotion } from "./EmotionBadge";

interface VideoFeed {
    studentName: string;
    emotion: Emotion;
    confidence: number;
    duration: string;
    isLive: boolean;
    studentId: string;
}

const initialFeeds: VideoFeed[] = mockStudents.slice(0, 6).map((s) => ({
    studentName: s.name,
    emotion: s.emotion,
    confidence: Math.floor(Math.random() * 20) + 75,
    duration: `${Math.floor(Math.random() * 40) + 10}:${Math.floor(Math.random() * 59).toString().padStart(2, "0")}`,
    isLive: Math.random() > 0.3,
    studentId: s.id
}));

export default function VideoAnalysis() {
    const [feeds, setFeeds] = useState<VideoFeed[]>(initialFeeds);
    const [selectedFeed, setSelectedFeed] = useState<number>(0);
    const feed = feeds[selectedFeed];

    // ─── Live Data Polling (Teacher Dashboard) ──────────────────────────
    useEffect(() => {
        const pollInterval = setInterval(async () => {
            try {
                const res = await fetch("http://localhost:8000/session-status/st1");
                if (res.ok) {
                    const data = await res.json();
                    if (data.error) return;

                    let state = data.state.toLowerCase();
                    let normalizedState: Emotion = "Calm";

                    if (state === "focused" || state === "working") normalizedState = "Focused";
                    else if (state === "confused") normalizedState = "Confused";
                    else if (state === "stressed") normalizedState = "Stressed";
                    else normalizedState = "Calm";

                    setFeeds(prev => prev.map(f => {
                        if (f.studentId === "st1") {
                            return {
                                ...f,
                                emotion: normalizedState,
                                confidence: Math.round(data.confidence * 100),
                                isLive: true
                            };
                        }
                        return f;
                    }));
                }
            } catch (err) {
                console.error("Polling failed:", err);
            }
        }, 1000);

        return () => clearInterval(pollInterval);
    }, []);

    return (
        <div>
            {/* Main Video Feed */}
            <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 overflow-hidden mb-6">
                <div className="flex">
                    {/* Video Area */}
                    <div className="flex-1 bg-[#1A1A2E] relative" style={{ minHeight: 400 }}>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <div className="w-20 h-20 rounded-full bg-[#2A2A3E] flex items-center justify-center mb-3 animate-pulse">
                                <span className="text-4xl">🎥</span>
                            </div>
                            <p className="text-white font-extrabold text-lg">{feed.studentName}</p>
                            <p className="text-[#AFAFAF] text-xs font-bold mt-1">
                                {feed.studentId === "st1" ? "Live AI Analysis Active" : "Video feed preview"}
                            </p>
                        </div>

                        {/* Live badge */}
                        {feed.isLive && (
                            <div className="absolute top-4 left-4 flex items-center gap-1.5 bg-[#FF4B4B] px-3 py-1.5 rounded-full z-10">
                                <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                                <span className="text-[10px] font-extrabold text-white uppercase tracking-wider">Live</span>
                            </div>
                        )}

                        {/* Duration */}
                        <div className="absolute top-4 right-4 bg-[#0D0D1A] bg-opacity-80 px-3 py-1.5 rounded-full z-10">
                            <span className="text-xs font-bold text-white">⏱️ {feed.duration}</span>
                        </div>

                        {/* Emotion Overlay */}
                        <div className="absolute bottom-4 left-4 right-4 z-10">
                            <div className="bg-[#0D0D1A] bg-opacity-90 rounded-2xl p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-[#58CC02] bg-[#F0FFF0]">
                                        <Image src={pingoAvatars[feed.emotion]} alt="Emotion" width={48} height={48} className="object-cover" />
                                    </div>
                                    <div>
                                        <p className="text-white font-extrabold text-sm capitalize">{feed.studentId === "st1" ? "Real-time Behavior" : "Detected Emotion"}</p>
                                        <EmotionBadge emotion={feed.emotion} />
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">Confidence</p>
                                    <p className="text-2xl font-black text-[#58CC02]">{feed.confidence}%</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Side Panel — Emotion Timeline */}
                    <div className="w-72 border-l-2 border-[#E5E5E5] bg-white">
                        <div className="p-4 border-b-2 border-[#E5E5E5]">
                            <h3 className="text-sm font-extrabold text-[#3C3C3C]">🧠 Emotion Timeline</h3>
                        </div>
                        <div className="p-4 space-y-3 overflow-y-auto" style={{ maxHeight: 340 }}>
                            {["Calm", "Focused", "Focused", "Confused", "Focused", "Stressed", "Calm", "Focused"].map((em, i) => (
                                <div key={i} className="flex items-center gap-2 p-2 rounded-xl bg-[#F7F7F7]">
                                    <Image src={pingoAvatars[em as Emotion]} alt={em} width={24} height={24} className="rounded-full" />
                                    <div className="flex-1">
                                        <p className="text-xs font-extrabold text-[#3C3C3C]">{em}</p>
                                        <p className="text-[10px] font-bold text-[#AFAFAF]">{i * 5}:{(i * 7 % 60).toString().padStart(2, "0")} min</p>
                                    </div>
                                    <div className="w-12 h-2 rounded-full bg-[#E5E5E5] overflow-hidden">
                                        <div className="h-full rounded-full" style={{
                                            width: `${60 + Math.random() * 40}%`,
                                            backgroundColor: em === "Stressed" ? "#FF4B4B" : em === "Confused" ? "#CE82FF" : em === "Focused" ? "#1CB0F6" : "#58CC02"
                                        }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* Student Feed Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                {feeds.map((f, i) => (
                    <button
                        key={i}
                        onClick={() => setSelectedFeed(i)}
                        className={`bg-white rounded-2xl border-2 border-b-4 p-4 text-left transition-all duration-100 hover:border-b-2 hover:mt-[2px] ${selectedFeed === i ? "border-[#1CB0F6]" : "border-[#E5E5E5]"
                            }`}
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-[#E5E5E5] bg-[#F7F7F7]">
                                <Image src={pingoAvatars[f.emotion]} alt={f.emotion} width={40} height={40} className="object-cover" />
                            </div>
                            <div>
                                <p className="text-sm font-extrabold text-[#3C3C3C]">{f.studentName}</p>
                                <p className="text-[10px] font-bold text-[#AFAFAF]">⏱️ {f.duration}</p>
                            </div>
                            {f.isLive && (
                                <div className="ml-auto flex items-center gap-1">
                                    <div className="w-2 h-2 rounded-full bg-[#FF4B4B] animate-pulse" />
                                    <span className="text-[9px] font-extrabold text-[#FF4B4B] uppercase">Live</span>
                                </div>
                            )}
                        </div>
                        <div className="flex items-center justify-between">
                            <EmotionBadge emotion={f.emotion} />
                            <span className="text-xs font-extrabold text-[#58CC02]">{f.confidence}%</span>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}
