"use client";

import React from "react";

export type Emotion = "Stressed" | "Focused" | "Confused" | "Calm";

const emotionConfig: Record<Emotion, { bg: string; emoji: string }> = {
    Stressed: { bg: "bg-[#FF4B4B]", emoji: "😰" },
    Focused: { bg: "bg-[#1CB0F6]", emoji: "🎯" },
    Confused: { bg: "bg-[#CE82FF]", emoji: "🤔" },
    Calm: { bg: "bg-[#58CC02]", emoji: "😌" },
};

interface EmotionBadgeProps {
    emotion: Emotion;
}

export default function EmotionBadge({ emotion }: EmotionBadgeProps) {
    const config = emotionConfig[emotion];
    return (
        <span
            className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-white text-sm font-extrabold uppercase tracking-wide ${config.bg} shadow-md`}
        >
            <span className="text-base">{config.emoji}</span>
            {emotion}
        </span>
    );
}
