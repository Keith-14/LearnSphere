"use client";

import React from "react";
import Image from "next/image";

interface ChatBubbleProps {
    role: "user" | "assistant";
    content: string;
    timestamp: string;
}

export default function ChatBubble({ role, content, timestamp }: ChatBubbleProps) {
    const isUser = role === "user";

    return (
        <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
            {!isUser && (
                <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center mr-2 mt-1 flex-shrink-0 border-2 border-[#E5E5E5] overflow-hidden">
                    <Image src="/pingo_logo.png" alt="Pingo" width={36} height={36} className="object-cover" />
                </div>
            )}
            <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${isUser
                    ? "bg-[#DDF4FF] text-[#3C3C3C] border-2 border-[#1CB0F6] rounded-br-lg"
                    : "bg-white text-[#3C3C3C] border-2 border-[#E5E5E5] rounded-bl-lg"
                    }`}
            >
                <p className="text-sm font-bold leading-relaxed">{content}</p>
                <p className={`text-[10px] mt-1.5 font-bold ${isUser ? "text-[#1CB0F6]" : "text-[#AFAFAF]"}`}>
                    {timestamp}
                </p>
            </div>
            {isUser && (
                <div className="w-9 h-9 rounded-full bg-[#FFC800] flex items-center justify-center ml-2 mt-1 flex-shrink-0 border-2 border-[#E5A600]">
                    <span className="text-white text-sm">😊</span>
                </div>
            )}
        </div>
    );
}
