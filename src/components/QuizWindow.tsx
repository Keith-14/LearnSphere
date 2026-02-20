"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { examQuestions, pingoAvatars } from "@/lib/mockData";
import type { Emotion } from "./EmotionBadge";
import EmotionBadge from "./EmotionBadge";

interface QuizWindowProps {
    onClose: () => void;
}

type QuizStep = "SelectExam" | "TakingQuiz" | "Results";

export default function QuizWindow({ onClose }: QuizWindowProps) {
    const [step, setStep] = useState<QuizStep>("SelectExam");
    const [selectedExam, setSelectedExam] = useState<string>("");
    const [currentQ, setCurrentQ] = useState(0);
    const [selectedOption, setSelectedOption] = useState<number | null>(null);
    const [answered, setAnswered] = useState(false);
    const [score, setScore] = useState(0);
    const [emotion, setEmotion] = useState<Emotion>("Calm");
    const [stressScore, setStressScore] = useState(0.0);
    const [isStable, setIsStable] = useState(true);
    const [timer, setTimer] = useState(600); // 10 minutes in seconds
    const [isTimerRunning, setIsTimerRunning] = useState(false);

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const questions = selectedExam ? examQuestions[selectedExam] : [];
    const question = questions[currentQ];

    // ─── Timer Logic ───────────────────────────────────────────────
    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isTimerRunning && timer > 0) {
            interval = setInterval(() => {
                setTimer((t) => t - 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [isTimerRunning, timer]);

    // ─── Video Intelligence Loop ──────────────────────────────────────────
    useEffect(() => {
        if (step === "SelectExam") return; // Don't start camera until quiz starts

        // 1. Initialize Webcam
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
                .then(stream => {
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                    }
                })
                .catch(err => console.error("Camera access denied:", err));
        }

        // 2. Set up analysis loop (every 600ms)
        const analysisInterval = setInterval(async () => {
            if (!videoRef.current || !canvasRef.current || step !== "TakingQuiz") return;

            const video = videoRef.current;
            const canvas = canvasRef.current;
            const context = canvas.getContext("2d");

            if (context && video.readyState === 4) {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                const imageData = canvas.toDataURL("image/jpeg", 0.6);

                try {
                    const res = await fetch("http://localhost:8000/analyze-frame", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ image: imageData })
                    });

                    if (res.ok) {
                        const data = await res.json();
                        // Map backend states to our Emotion type
                        // Backend states: calm, focused, confused, stressed, working
                        let state = data.state.toLowerCase();
                        let normalizedState: Emotion = "Calm";

                        if (state === "focused" || state === "working") normalizedState = "Focused";
                        else if (state === "confused") normalizedState = "Confused";
                        else if (state === "stressed") normalizedState = "Stressed";
                        else normalizedState = "Calm";

                        setEmotion(normalizedState);
                        setStressScore(data.stress_score);
                        setIsStable(data.is_stable);
                    }
                } catch (err) {
                    console.error("Frame analysis failed:", err);
                }
            }
        }, 600);

        return () => {
            clearInterval(analysisInterval);
            if (videoRef.current && videoRef.current.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [step]);

    const formatTime = (s: number) => {
        const m = Math.floor(s / 60).toString().padStart(2, "0");
        const sec = (s % 60).toString().padStart(2, "0");
        return `${m}:${sec}`;
    };

    const handleStartQuiz = (exam: string) => {
        setSelectedExam(exam);
        setStep("TakingQuiz");
        setIsTimerRunning(true);
    };

    const handleSelect = (idx: number) => {
        if (answered) return;
        setSelectedOption(idx);
        setAnswered(true);
        if (idx === question.correctIndex) {
            setScore((s) => s + 1);
        }
    };

    const handleNext = () => {
        if (currentQ + 1 >= questions.length) {
            setStep("Results");
            setIsTimerRunning(false);
        } else {
            setCurrentQ((q) => q + 1);
            setSelectedOption(null);
            setAnswered(false);
        }
    };

    // ─── Step 1: Select Exam ────────────────────────────────────────
    if (step === "SelectExam") {
        const exams = [
            { id: "GRE", name: "GRE", desc: "Graduate Record Examinations", icon: "🎓" },
            { id: "JEE", name: "JEE", desc: "Joint Entrance Examination", icon: "🔬" },
            { id: "GMAT", name: "GMAT", desc: "Graduate Management Admission Test", icon: "📊" },
            { id: "CAT", name: "CAT", desc: "Common Admission Test", icon: "📉" },
            { id: "SAT", name: "SAT", desc: "Scholastic Assessment Test", icon: "📚" }
        ];

        return (
            <div className="bg-white rounded-3xl border-2 border-[#E5E5E5] border-b-8 p-10 max-w-4xl mx-auto shadow-xl">
                <div className="text-center mb-10">
                    <div className="w-20 h-20 bg-[#F0FFF0] rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-[#58CC02]">
                        <Image src="/pingo_confident.png" alt="Pingo" width={60} height={60} />
                    </div>
                    <h1 className="text-4xl font-black text-[#3C3C3C] mb-2">Choose Your Challenge</h1>
                    <p className="text-[#AFAFAF] font-bold text-lg">Select an exam to start your AI-monitored study session.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {exams.map((exam) => (
                        <button
                            key={exam.id}
                            onClick={() => handleStartQuiz(exam.id)}
                            className="group p-6 rounded-2xl border-2 border-[#E5E5E5] border-b-6 hover:border-[#1CB0F6] hover:bg-[#F0F9FF] transition-all text-left active:border-b-2 active:mt-1"
                        >
                            <span className="text-4xl mb-4 block group-hover:scale-110 transition-transform">{exam.icon}</span>
                            <h3 className="text-xl font-black text-[#3C3C3C] mb-1">{exam.name}</h3>
                            <p className="text-sm font-bold text-[#AFAFAF] leading-tight">{exam.desc}</p>
                        </button>
                    ))}
                </div>

                <div className="mt-10 pt-8 border-t-2 border-[#F7F7F7] flex justify-center">
                    <button onClick={onClose} className="px-8 py-3 rounded-xl border-2 border-[#E5E5E5] text-[#AFAFAF] font-black uppercase text-sm hover:bg-[#F7F7F7] transition-colors">
                        Cancel & Close
                    </button>
                </div>
            </div>
        );
    }

    // ─── Step 3: Results ───────────────────────────────────────────
    if (step === "Results") {
        const pct = Math.round((score / questions.length) * 100);
        return (
            <div className="bg-white rounded-3xl border-2 border-[#E5E5E5] border-b-8 p-12 text-center max-w-2xl mx-auto shadow-2xl">
                <div className="relative inline-block mb-8">
                    <div className="absolute -inset-4 bg-[#58CC02]/10 rounded-full animate-ping" />
                    <Image
                        src={pct >= 70 ? "/pingo_happy.png" : "/pingo_thinking.png"}
                        alt="Result"
                        width={160}
                        height={160}
                        className="relative z-10 mx-auto"
                    />
                </div>

                <h2 className="text-4xl font-black text-[#3C3C3C] mb-4">
                    {pct >= 90 ? "Legendary! 🌟" : pct >= 70 ? "Excellent! 🎉" : pct >= 50 ? "Solid Effort! 👍" : "Keep at it! 💪"}
                </h2>

                <div className="flex justify-center items-baseline gap-2 mb-2">
                    <span className="text-7xl font-black" style={{ color: pct >= 70 ? "#58CC02" : pct >= 50 ? "#FFC800" : "#FF4B4B" }}>
                        {score}
                    </span>
                    <span className="text-2xl font-black text-[#AFAFAF]">/ {questions.length}</span>
                </div>

                <p className="text-xl font-bold text-[#AFAFAF] mb-10">
                    You scored {pct}% with {formatTime(600 - timer)} left on the clock.
                </p>

                <div className="grid grid-cols-2 gap-4">
                    <button onClick={onClose} className="px-8 py-4 rounded-2xl border-2 border-[#E5E5E5] border-b-4 text-[#3C3C3C] font-black uppercase hover:bg-[#F7F7F7] active:border-b-0 active:mt-1 transition-all">
                        Exit Session
                    </button>
                    <button
                        onClick={() => { setStep("SelectExam"); setCurrentQ(0); setScore(0); setSelectedOption(null); setAnswered(false); setTimer(600); setEmotion("Calm"); }}
                        className="px-8 py-4 rounded-2xl bg-[#58CC02] border-b-4 border-[#46A302] text-white font-black uppercase shadow-lg shadow-[#58CC02]/20 active:border-b-0 active:mt-1 transition-all"
                    >
                        New Quiz
                    </button>
                </div>
            </div>
        );
    }

    // ─── Step 2: Taking Quiz ────────────────────────────────────────
    return (
        <div className="max-w-6xl mx-auto px-4">
            <canvas ref={canvasRef} style={{ display: "none" }} />

            {/* Video logic is now integrated into the header below */}

            <div className="bg-white rounded-3xl border-2 border-[#E5E5E5] border-b-8 overflow-hidden shadow-xl">
                {/* Header */}
                <div className="bg-[#F7F7F7] px-8 py-6 border-b-2 border-[#E5E5E5] flex items-center justify-between">
                    <div className="flex items-center gap-5">
                        <div className="w-14 h-14 bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 flex items-center justify-center">
                            <span className="text-2xl">⚡</span>
                        </div>
                        <div>
                            <h2 className="text-2xl font-black text-[#3C3C3C]">{selectedExam} Mastery</h2>
                            <p className="text-sm font-bold text-[#AFAFAF]">Question {currentQ + 1} of {questions.length}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-8">
                        {/* Video Panel Integrated Here - Micro footprint */}
                        <div className="flex flex-col items-end gap-2">
                            <div className="w-32 h-20 rounded-xl overflow-hidden relative border-2 border-[#3C3C3C] bg-black shadow-lg">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    className="w-full h-full object-cover"
                                />
                                <div className="absolute top-1 right-1 flex items-center gap-1 bg-[#FF4B4B] px-1 py-0.5 rounded-full text-[5px] font-black text-white uppercase tracking-wider">
                                    <div className="w-1 h-1 rounded-full bg-white animate-pulse" />
                                    LIVE
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-[9px] font-black text-[#AFAFAF] uppercase tracking-widest mb-0.5">Remaining</p>
                                <span className={`text-xl font-black font-mono leading-none ${timer < 60 ? "text-[#FF4B4B] animate-pulse" : "text-[#3C3C3C]"}`}>
                                    {formatTime(timer)}
                                </span>
                            </div>
                        </div>
                        <button onClick={onClose} className="px-5 py-2 rounded-xl border-2 border-[#FFDFE0] text-[#FF4B4B] font-black text-sm uppercase hover:bg-[#FFDFE0] transition-all">
                            Quit
                        </button>
                    </div>
                </div>

                {/* Question Area */}
                <div className="p-10">
                    <div className="mb-8">
                        <span className="px-4 py-1.5 bg-[#F0F9FF] border-2 border-[#1CB0F6] rounded-xl text-[#1CB0F6] text-xs font-black uppercase tracking-wider">
                            {question.topic}
                        </span>
                    </div>

                    <h3 className="text-2xl font-black text-[#3C3C3C] leading-snug mb-10">
                        {question.question}
                    </h3>

                    <div className="grid grid-cols-1 gap-4 mb-10">
                        {question.options.map((opt, idx) => {
                            let style = "border-[#E5E5E5] border-b-6 hover:bg-[#F7F7F7] text-[#3C3C3C]";
                            if (answered) {
                                if (idx === question.correctIndex) {
                                    style = "bg-[#D7FFB8] border-[#58CC02] border-b-6 text-[#1E4D00]";
                                } else if (idx === selectedOption) {
                                    style = "bg-[#FFDFE0] border-[#FF4B4B] border-b-6 text-[#7B1D21]";
                                } else {
                                    style = "opacity-40 border-[#E5E5E5] border-b-2 grayscale-[0.5]";
                                }
                            } else if (idx === selectedOption) {
                                style = "bg-[#F0F9FF] border-[#1CB0F6] border-b-6 text-[#1CB0F6]";
                            }

                            return (
                                <button
                                    key={idx}
                                    onClick={() => handleSelect(idx)}
                                    disabled={answered}
                                    className={`relative group px-8 py-5 rounded-2xl border-2 font-black text-lg transition-all text-left flex items-center gap-6 ${style} ${!answered ? "active:border-b-2 active:mt-1" : ""}`}
                                >
                                    <span className={`w-10 h-10 rounded-xl border-2 flex items-center justify-center text-sm font-black flex-shrink-0 transition-colors
                                        ${style.includes("bg-[#D7FFB8]") ? "bg-white/40 border-[#58CC02]" :
                                            style.includes("bg-[#FFDFE0]") ? "bg-white/40 border-[#FF4B4B]" :
                                                style.includes("bg-[#F0F9FF]") ? "bg-white/40 border-[#1CB0F6]" : "bg-white border-[#E5E5E5] text-[#AFAFAF]"}
                                    `}>
                                        {String.fromCharCode(65 + idx)}
                                    </span>
                                    <span className="flex-1">{opt}</span>
                                    {answered && idx === question.correctIndex && <span className="text-2xl">✅</span>}
                                    {answered && idx === selectedOption && idx !== question.correctIndex && <span className="text-2xl">❌</span>}
                                </button>
                            );
                        })}
                    </div>

                    {/* Progress & Actions */}
                    <div className="flex items-center justify-between gap-10">
                        <div className="flex-1">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-xs font-black text-[#AFAFAF] uppercase tracking-widest">Course Progress</span>
                                <span className="text-xs font-black text-[#58CC02]">{Math.round(((currentQ + (answered ? 1 : 0)) / questions.length) * 100)}%</span>
                            </div>
                            <div className="h-4 bg-[#F7F7F7] rounded-full p-1 border-2 border-[#E5E5E5]">
                                <div
                                    className="h-full bg-[#58CC02] rounded-full transition-all duration-700 shadow-[0_0_10px_rgba(88,204,2,0.3)]"
                                    style={{ width: `${((currentQ + (answered ? 1 : 0)) / questions.length) * 100}%` }}
                                />
                            </div>
                        </div>

                        {answered && (
                            <button
                                onClick={handleNext}
                                className="px-10 py-4 rounded-2xl bg-[#58CC02] border-b-8 border-[#46A302] text-white font-black uppercase text-sm tracking-widest shadow-xl shadow-[#58CC02]/20 active:border-b-0 active:mt-2 transition-all hover:brightness-110 flex items-center gap-3"
                            >
                                {currentQ + 1 === questions.length ? "Finish Session" : "Next Question"}
                                <span>→</span>
                            </button>
                        )}
                    </div>
                </div>
            </div>

        </div>
    );
}
