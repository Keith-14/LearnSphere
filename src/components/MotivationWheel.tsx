"use client";

import React, { useState } from "react";
import Image from "next/image";

interface WheelSlice {
    label: string;
    color: string;
    question: string;
}

const slices: WheelSlice[] = [
    { label: "Quant Mastery", color: "#A8D121", question: "If you had to solve a complex Probability question right now, which concept would you rely on most?" },
    { label: "Verbal Precision", color: "#F08C2D", question: "What's one sophisticated word you learned recently that would impress a GMAT/CAT examiner?" },
    { label: "Logical Depth", color: "#D2364E", question: "Can you identify a logical fallacy in a recent argument you heard or read?" },
    { label: "Data Insight", color: "#A14DA1", question: "How would you visualize the progress of your study sessions using a single chart type?" },
    { label: "Physics Logic", color: "#74459C", question: "Which law of physics fascinates you the most when applied to engineering marvels?" },
    { label: "Organic Flow", color: "#3B59DA", question: "If a chemical reaction represented your study flow, would it be exothermic or endothermic?" },
    { label: "Calculus Edge", color: "#1CB0F6", question: "What is the 'rate of change' of your confidence level since you started this prep?" },
    { label: "Critical Thinking", color: "#1EB2A6", question: "How would you deconstruct a complex problem into three smaller, manageable pieces?" },
    { label: "Mock Strategy", color: "#169B45", question: "What is your #1 strategy for handling a question that seems impossible at first glance?" },
    { label: "Exam Zen", color: "#3D8E33", question: "How do you plan to maintain your composure during the most high-pressure 10 minutes of the exam?" },
];

export default function MotivationWheel() {
    const [rotation, setRotation] = useState(0);
    const [isSpinning, setIsSpinning] = useState(false);
    const [selectedSlice, setSelectedSlice] = useState<WheelSlice | null>(null);

    const spinWheel = () => {
        if (isSpinning) return;

        setIsSpinning(true);
        setSelectedSlice(null);

        const extraSpins = 8 + Math.random() * 5;
        const newRotation = rotation + extraSpins * 360;
        setRotation(newRotation);

        setTimeout(() => {
            setIsSpinning(false);
            const actualDegree = newRotation % 360;
            const sliceIndex = Math.floor(((360 - (actualDegree % 360)) % 360) / (360 / 10));
            setSelectedSlice(slices[sliceIndex]);
        }, 5000);
    };

    return (
        <div className="w-full max-w-[90vw] mx-auto p-4 md:p-10 flex flex-col items-center min-h-[80vh] justify-center">
            <div className="text-center mb-16">
                <h1 className="text-5xl font-black text-[#3C3C3C] mb-4 tracking-tight">Exam Mastery Spark 🎡</h1>
                <p className="text-[#AFAFAF] font-bold text-xl max-w-2xl mx-auto leading-relaxed">
                    Tailored for <span className="text-[#1CB0F6]">CAT / GMAT / JEE</span>. Spin the wheel to sharpen your mindset and conquer the next topic.
                </p>
            </div>

            <div className="w-full flex flex-col lg:flex-row items-center justify-around gap-12 bg-white p-6 md:p-16 rounded-[60px] border-2 border-[#E5E5E5] border-b-[12px] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.1)] relative overflow-hidden min-h-[600px]">
                {/* Background Gradient */}
                <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-[#1CB0F6]/5 to-transparent pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-1/4 h-1/2 bg-gradient-to-tr from-[#58CC02]/5 to-transparent pointer-events-none" />

                {/* The Wheel Container */}
                <div className="relative group perspective-1000">
                    {/* Shadow underneath */}
                    <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-[80%] h-10 bg-black/5 blur-3xl rounded-full" />

                    {/* Pointer */}
                    <div className="absolute right-[-25px] top-1/2 -translate-y-1/2 z-20 w-12 h-12 flex items-center justify-center">
                        <div className="w-0 h-0 border-l-[25px] border-l-transparent border-r-[25px] border-r-transparent border-t-[35px] border-t-[#3C3C3C] -rotate-90 hover:scale-110 transition-transform cursor-pointer drop-shadow-xl" />
                    </div>

                    <div
                        className="w-[380px] h-[380px] md:w-[520px] md:h-[520px] relative transition-transform duration-[5000ms] cubic-bezier(0.2, 0, 0, 1) cursor-pointer"
                        style={{ transform: `rotate(${rotation}deg)` }}
                        onClick={spinWheel}
                    >
                        <svg viewBox="0 0 100 100" className="w-full h-full drop-shadow-[0_20px_40px_rgba(0,0,0,0.15)]">
                            {slices.map((slice, i) => {
                                const angle = (360 / slices.length);
                                const startAngle = i * angle;
                                const endAngle = (i + 1) * angle;

                                const x1 = 50 + 50 * Math.cos((Math.PI * startAngle) / 180);
                                const y1 = 50 + 50 * Math.sin((Math.PI * startAngle) / 180);
                                const x2 = 50 + 50 * Math.cos((Math.PI * endAngle) / 180);
                                const y2 = 50 + 50 * Math.sin((Math.PI * endAngle) / 180);

                                return (
                                    <g key={slice.label}>
                                        <path
                                            d={`M 50 50 L ${x1} ${y1} A 50 50 0 0 1 ${x2} ${y2} Z`}
                                            fill={slice.color}
                                            stroke="white"
                                            strokeWidth="0.8"
                                            className="hover:brightness-110 transition-all"
                                        />
                                        <g transform={`rotate(${startAngle + angle / 2}, 50, 50)`}>
                                            <text
                                                x="78"
                                                y="50.5"
                                                fill="white"
                                                fontSize="2.2"
                                                fontWeight="900"
                                                textAnchor="end"
                                                className="uppercase tracking-tighter"
                                                style={{ textShadow: "0px 1px 3px rgba(0,0,0,0.4)" }}
                                            >
                                                {slice.label}
                                            </text>
                                        </g>
                                    </g>
                                );
                            })}
                            <circle cx="50" cy="50" r="12" fill="#3C3C3C" stroke="white" strokeWidth="3" />
                            <circle cx="50" cy="50" r="3" fill="white" />
                        </svg>
                    </div>

                    {/* Spin Label at Center */}
                    <button
                        onClick={spinWheel}
                        disabled={isSpinning}
                        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-24 h-24 rounded-full bg-white border-4 border-[#3C3C3C] shadow-2xl flex flex-col items-center justify-center hover:scale-105 transition-all active:scale-95 disabled:opacity-50 ring-8 ring-white/30"
                    >
                        <span className="text-[12px] font-black text-[#3C3C3C] uppercase text-center block leading-none">
                            {isSpinning ? "GO!" : "Fast"}
                        </span>
                        {!isSpinning && <span className="text-[10px] font-bold text-[#AFAFAF] uppercase mt-1">Spin</span>}
                    </button>
                </div>

                {/* Results Panel */}
                <div className="flex-1 w-full max-w-md bg-[#FBFBFB] p-10 rounded-[40px] border-2 border-[#E5E5E5] group-hover:border-[#1CB0F6] transition-colors relative h-fit shadow-inner">
                    {selectedSlice ? (
                        <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                            <div className="flex items-center gap-5 mb-8">
                                <div className="w-20 h-20 rounded-[24px] flex items-center justify-center text-4xl shadow-2xl animate-bounce-subtle" style={{ backgroundColor: selectedSlice.color, color: "white" }}>
                                    🎯
                                </div>
                                <div>
                                    <span className="text-[10px] font-black uppercase tracking-[0.2em]" style={{ color: selectedSlice.color }}>
                                        {selectedSlice.label}
                                    </span>
                                    <h2 className="text-4xl font-extrabold text-[#3C3C3C] tracking-tight">Active Spark</h2>
                                </div>
                            </div>

                            <div className="bg-white p-10 rounded-[32px] border-2 border-[#E5E5E5] relative shadow-lg">
                                <div className="absolute -left-3 top-10 w-6 h-6 bg-white border-l-2 border-b-2 border-[#E5E5E5] rotate-45" />
                                <p className="text-2xl font-black text-[#3C3C3C] leading-[1.6]">
                                    "{selectedSlice.question}"
                                </p>
                            </div>

                            <button
                                onClick={spinWheel}
                                className="mt-10 w-full py-5 rounded-2xl bg-[#3C3C3C] text-white font-black uppercase tracking-widest hover:bg-black transition-all active:scale-95 shadow-xl"
                            >
                                Spin Again →
                            </button>
                        </div>
                    ) : (
                        <div className="text-center lg:text-left py-12">
                            <h2 className="text-5xl font-black text-[#3C3C3C] mb-6 leading-tight">Ignite Your Focus.</h2>
                            <p className="text-xl font-bold text-[#AFAFAF] leading-relaxed mb-10">
                                Break the monotony of study. Get a challenge tailored for your competitive journey.
                            </p>
                            <button
                                onClick={spinWheel}
                                disabled={isSpinning}
                                className="w-full py-6 rounded-3xl bg-[#58CC02] border-b-8 border-[#46A302] text-white font-black uppercase tracking-widest text-xl shadow-2xl shadow-[#58CC02]/30 hover:brightness-110 transition-all active:border-b-0 active:translate-y-2"
                            >
                                {isSpinning ? "CALCULATING..." : "SPARK MOCK DRILL ✨"}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
