"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { mockQuizQuestions, pingoAvatars } from "@/lib/mockData";
import type { Emotion } from "./EmotionBadge";
import EmotionBadge from "./EmotionBadge";

interface QuizWindowProps {
    onClose: () => void;
}

export default function QuizWindow({ onClose }: QuizWindowProps) {
    const [currentQ, setCurrentQ] = useState(0);
    const [selected, setSelected] = useState<number | null>(null);
    const [answered, setAnswered] = useState(false);
    const [score, setScore] = useState(0);
    const [quizDone, setQuizDone] = useState(false);
    const [emotion, setEmotion] = useState<Emotion>("Calm");
    const [timer, setTimer] = useState(0);

    const question = mockQuizQuestions[currentQ];

    useEffect(() => {
        const interval = setInterval(() => setTimer((t) => t + 1), 1000);
        return () => clearInterval(interval);
    }, []);

    const formatTime = (s: number) => {
        const m = Math.floor(s / 60).toString().padStart(2, "0");
        const sec = (s % 60).toString().padStart(2, "0");
        return `${m}:${sec}`;
    };

    const handleSelect = (idx: number) => {
        if (answered) return;
        setSelected(idx);
        setAnswered(true);
        const correct = idx === question.correctIndex;
        if (correct) {
            setScore((s) => s + 1);
            setEmotion("Focused");
        } else {
            if (currentQ >= 2) setEmotion("Stressed");
            else setEmotion("Confused");
        }
    };

    const handleNext = () => {
        if (currentQ + 1 >= mockQuizQuestions.length) {
            setQuizDone(true);
            const pct = ((score + (selected === question.correctIndex ? 0 : 0)) / mockQuizQuestions.length) * 100;
            if (pct >= 80) setEmotion("Calm");
            else if (pct >= 60) setEmotion("Focused");
            else setEmotion("Stressed");
        } else {
            setCurrentQ((q) => q + 1);
            setSelected(null);
            setAnswered(false);
        }
    };

    if (quizDone) {
        const pct = Math.round((score / mockQuizQuestions.length) * 100);
        return (
            <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 p-8 text-center">
                <Image src={pct >= 60 ? pingoAvatars["Calm"] : pingoAvatars["Stressed"]} alt="Result" width={120} height={120} className="mx-auto mb-4" />
                <h2 className="text-3xl font-black text-[#3C3C3C] mb-2">
                    {pct >= 80 ? "Amazing! 🎉" : pct >= 60 ? "Good job! 👍" : "Keep practicing! 💪"}
                </h2>
                <p className="text-5xl font-black mb-2" style={{ color: pct >= 80 ? "#58CC02" : pct >= 60 ? "#FFC800" : "#FF4B4B" }}>
                    {score}/{mockQuizQuestions.length}
                </p>
                <p className="text-[#AFAFAF] font-bold mb-6">You scored {pct}% in {formatTime(timer)}</p>
                <div className="flex gap-3 justify-center">
                    <button onClick={onClose} className="px-6 py-3 rounded-xl border-2 border-[#E5E5E5] text-[#3C3C3C] font-extrabold text-sm hover:bg-[#F7F7F7] transition-colors">
                        Back to Dashboard
                    </button>
                    <button onClick={() => { setCurrentQ(0); setScore(0); setSelected(null); setAnswered(false); setQuizDone(false); setTimer(0); setEmotion("Calm"); }}
                        className="px-6 py-3 rounded-xl bg-[#58CC02] border-b-4 border-[#46A302] text-white font-extrabold text-sm uppercase active:border-b-0 active:mt-1 transition-all">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="relative">
            {/* Camera Corner — Fixed Top Right of viewport */}
            <div className="fixed top-3 right-3 z-50">
                <div className="w-48 h-36 rounded-2xl overflow-hidden relative shadow-2xl border-2 border-[#3C3C3C]">
                    {/* Simulated video feed background */}
                    <div className="absolute inset-0 bg-gradient-to-br from-[#1A1A2E] via-[#2D2D44] to-[#1A1A2E]">
                        <div className="absolute inset-0 opacity-30" style={{
                            backgroundImage: "radial-gradient(circle at 30% 40%, #4a4a6a 0%, transparent 50%), radial-gradient(circle at 70% 60%, #3a3a5a 0%, transparent 40%)",
                        }} />
                        {/* Scanning line animation */}
                        <div className="absolute left-0 right-0 h-[2px] bg-[#1CB0F6] opacity-30 animate-pulse" style={{ top: "40%" }} />
                    </div>
                    {/* Face outline placeholder */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-16 h-16 rounded-full border-2 border-dashed border-[#AFAFAF] opacity-40" />
                    </div>
                    {/* Live indicator */}
                    <div className="absolute top-2 left-2 flex items-center gap-1.5 bg-[#FF4B4B] px-2 py-0.5 rounded-full">
                        <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                        <span className="text-[8px] font-extrabold text-white uppercase tracking-wider">Live</span>
                    </div>
                    {/* Emotion overlay */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
                        <div className="flex items-center gap-1.5">
                            <Image src={pingoAvatars[emotion]} alt="Emotion" width={18} height={18} className="rounded-full" />
                            <span className="text-[10px] font-extrabold text-white">{emotion}</span>
                            <div className="ml-auto w-10 h-1.5 rounded-full bg-[#3C3C3C] overflow-hidden">
                                <div className="h-full rounded-full bg-[#58CC02] animate-pulse" style={{ width: "75%" }} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 overflow-hidden">
                {/* Quiz Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b-2 border-[#E5E5E5]">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-[#58CC02] bg-[#F0FFF0]">
                            <Image src={pingoAvatars[emotion]} alt="Pingo" width={40} height={40} className="object-cover" />
                        </div>
                        <div>
                            <p className="text-xs font-extrabold text-[#AFAFAF] uppercase tracking-widest">Quiz Mode</p>
                            <p className="text-sm font-extrabold text-[#3C3C3C]">Question {currentQ + 1} of {mockQuizQuestions.length}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <EmotionBadge emotion={emotion} />
                        <span className="text-sm font-extrabold text-[#AFAFAF] bg-[#F7F7F7] px-3 py-1 rounded-full">⏱️ {formatTime(timer)}</span>
                        <button onClick={onClose} className="text-[#FF4B4B] hover:bg-[#FFF0F0] font-extrabold text-sm px-4 py-2 rounded-xl border-2 border-[#FF4B4B] transition-colors">
                            End Quiz
                        </button>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="px-6 pt-4">
                    <div className="h-3 rounded-full bg-[#E5E5E5] overflow-hidden">
                        <div
                            className="h-full rounded-full bg-[#58CC02] transition-all duration-500"
                            style={{ width: `${((currentQ + (answered ? 1 : 0)) / mockQuizQuestions.length) * 100}%` }}
                        />
                    </div>
                </div>

                {/* Question */}
                <div className="p-6">
                    <div className="mb-2">
                        <span className="text-xs font-extrabold text-[#AFAFAF] bg-[#F7F7F7] px-3 py-1 rounded-full border-2 border-[#E5E5E5]">
                            📚 {question.topic}
                        </span>
                    </div>
                    <h2 className="text-xl font-extrabold text-[#3C3C3C] mt-3 mb-6">{question.question}</h2>

                    {/* Options */}
                    <div className="space-y-3">
                        {question.options.map((opt, idx) => {
                            let optClass = "bg-white border-2 border-[#E5E5E5] border-b-4 hover:bg-[#F7F7F7] text-[#3C3C3C]";
                            if (answered) {
                                if (idx === question.correctIndex) {
                                    optClass = "bg-[#D7FFB8] border-2 border-[#58CC02] border-b-4 text-[#3C3C3C]";
                                } else if (idx === selected && idx !== question.correctIndex) {
                                    optClass = "bg-[#FFDFE0] border-2 border-[#FF4B4B] border-b-4 text-[#3C3C3C]";
                                } else {
                                    optClass = "bg-white border-2 border-[#E5E5E5] text-[#AFAFAF]";
                                }
                            } else if (idx === selected) {
                                optClass = "bg-[#DDF4FF] border-2 border-[#1CB0F6] border-b-4 text-[#3C3C3C]";
                            }

                            return (
                                <button
                                    key={idx}
                                    onClick={() => handleSelect(idx)}
                                    disabled={answered}
                                    className={`w-full text-left px-5 py-4 rounded-xl font-bold text-sm transition-all duration-100 flex items-center gap-3 ${optClass} ${!answered ? "active:border-b-2 active:mt-[2px] cursor-pointer" : ""}`}
                                >
                                    <span className="w-8 h-8 rounded-lg border-2 border-current flex items-center justify-center text-xs font-extrabold flex-shrink-0 opacity-60">
                                        {String.fromCharCode(65 + idx)}
                                    </span>
                                    {opt}
                                    {answered && idx === question.correctIndex && <span className="ml-auto text-lg">✅</span>}
                                    {answered && idx === selected && idx !== question.correctIndex && <span className="ml-auto text-lg">❌</span>}
                                </button>
                            );
                        })}
                    </div>

                    {/* Next Button */}
                    {answered && (
                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={handleNext}
                                className="px-8 py-3 rounded-xl bg-[#58CC02] border-b-4 border-[#46A302] text-white font-extrabold text-sm uppercase tracking-wide active:border-b-0 active:mt-1 transition-all"
                            >
                                {currentQ + 1 >= mockQuizQuestions.length ? "See Results" : "Next →"}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
