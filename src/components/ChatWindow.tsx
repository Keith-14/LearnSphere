"use client";

import React, { useState, useRef, useEffect } from "react";
import EmotionBadge from "./EmotionBadge";
import ChatBubble from "./ChatBubble";
import { ChatMessage, mockChatMessages } from "@/lib/mockData";
import type { Emotion } from "./EmotionBadge";

function detectEmotion(text: string): Emotion {
    const lower = text.toLowerCase();
    if (lower.includes("stuck") || lower.includes("difficult") || lower.includes("hard") || lower.includes("stressed") || lower.includes("overwhelm")) return "Stressed";
    if (lower.includes("focus") || lower.includes("got it") || lower.includes("great") || lower.includes("understand")) return "Focused";
    if (lower.includes("confused") || lower.includes("don't understand") || lower.includes("what") || lower.includes("why")) return "Confused";
    if (lower.includes("easy") || lower.includes("calm") || lower.includes("good") || lower.includes("relax")) return "Calm";
    return "Calm";
}

const assistantResponses: Record<Emotion, string> = {
    Stressed: "I can see this is tough! 💪 Let's break it down into smaller bites. You've got this!",
    Focused: "Amazing focus! 🎯 You're on fire! Let's tackle something even more challenging!",
    Confused: "No worries at all! 🌟 Let me explain it differently — we'll figure this out together!",
    Calm: "Great vibes! 😊 Let's keep cruising through this topic at your pace!",
};

interface ChatWindowProps {
    onClose: () => void;
}

export default function ChatWindow({ onClose }: ChatWindowProps) {
    const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
    const [input, setInput] = useState("");
    const [emotion, setEmotion] = useState<Emotion>("Calm");
    const [sessionTime, setSessionTime] = useState(0);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const interval = setInterval(() => setSessionTime((t) => t + 1), 1000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60).toString().padStart(2, "0");
        const s = (seconds % 60).toString().padStart(2, "0");
        return `${m}:${s}`;
    };

    const handleSend = () => {
        if (!input.trim()) return;
        const detectedEmotion = detectEmotion(input);
        setEmotion(detectedEmotion);

        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

        const userMsg: ChatMessage = {
            id: `m${messages.length + 1}`,
            role: "user",
            content: input,
            timestamp: timeStr,
        };

        const assistantMsg: ChatMessage = {
            id: `m${messages.length + 2}`,
            role: "assistant",
            content: assistantResponses[detectedEmotion],
            timestamp: timeStr,
        };

        setMessages((prev) => [...prev, userMsg, assistantMsg]);
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 flex flex-col h-[600px]">
            {/* Top Bar */}
            <div className="flex items-center justify-between px-6 py-4 border-b-2 border-[#E5E5E5]">
                <div className="flex items-center gap-3">
                    <EmotionBadge emotion={emotion} />
                    <span className="text-xs font-extrabold text-[#AFAFAF] bg-[#F7F7F7] px-3 py-1.5 rounded-full border-2 border-[#E5E5E5]">
                        ⚡ ADAPTIVE MODE
                    </span>
                </div>
                <div className="flex items-center gap-4">
                    <span className="text-sm font-extrabold text-[#AFAFAF] bg-[#F7F7F7] px-3 py-1 rounded-full">
                        ⏱️ {formatTime(sessionTime)}
                    </span>
                    <button
                        onClick={onClose}
                        className="text-[#FF4B4B] hover:bg-[#FFF0F0] font-extrabold text-sm px-4 py-2 rounded-xl border-2 border-[#FF4B4B] transition-colors"
                    >
                        End Session
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 bg-[#F7F7F7]">
                {messages.map((msg) => (
                    <ChatBubble key={msg.id} role={msg.role} content={msg.content} timestamp={msg.timestamp} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="px-6 py-4 border-t-2 border-[#E5E5E5]">
                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        placeholder="Type your answer..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className="flex-1 rounded-2xl border-2 border-[#E5E5E5] bg-white px-4 py-3 text-sm font-bold text-[#3C3C3C] placeholder:text-[#AFAFAF] focus:outline-none focus:border-[#58CC02] transition-colors"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim()}
                        className="bg-[#58CC02] hover:bg-[#46A302] disabled:bg-[#E5E5E5] disabled:text-[#AFAFAF] text-white px-6 py-3 rounded-2xl text-sm font-extrabold uppercase tracking-wide transition-colors border-b-4 border-[#46A302] disabled:border-[#D5D5D5] active:border-b-0 active:mt-1"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
