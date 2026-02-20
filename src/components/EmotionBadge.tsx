"use client";

import React from "react";
import Image from "next/image";
import { pingoAvatars } from "@/lib/mockData";

export type Emotion = "Stressed" | "Focused" | "Confused" | "Calm";

const emotionConfig: Record<Emotion, { bg: string }> = {
    Stressed: { bg: "bg-[#FF4B4B]" },
    Focused: { bg: "bg-[#1CB0F6]" },
    Confused: { bg: "bg-[#CE82FF]" },
    Calm: { bg: "bg-[#58CC02]" },
};

interface EmotionBadgeProps {
    emotion: Emotion;
    showAvatar?: boolean;
}

export default function EmotionBadge({ emotion, showAvatar = true }: EmotionBadgeProps) {
    const config = emotionConfig[emotion];
    return (
        <span
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-white text-sm font-extrabold uppercase tracking-wide ${config.bg} shadow-md`}
        >
            {showAvatar && (
                <Image
                    src={pingoAvatars[emotion]}
                    alt={emotion}
                    width={22}
                    height={22}
                    className="rounded-full"
                />
            )}
            {emotion}
        </span>
    );
}
