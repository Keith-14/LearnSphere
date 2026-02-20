"use client";

import React from "react";

interface MetricsCardProps {
    label: string;
    value: string;
    subtext?: string;
    icon: string;
    color?: string;
}

export default function MetricsCard({ label, value, subtext, icon, color = "#58CC02" }: MetricsCardProps) {
    return (
        <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 p-5 hover:border-b-2 hover:mt-[2px] transition-all duration-100 cursor-pointer">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-xs font-bold text-[#AFAFAF] uppercase tracking-wider">{label}</p>
                    <p className="mt-1 text-2xl font-extrabold" style={{ color }}>{value}</p>
                    {subtext && (
                        <p className="mt-1 text-xs font-bold text-[#AFAFAF]">{subtext}</p>
                    )}
                </div>
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl" style={{ backgroundColor: `${color}20` }}>
                    {icon}
                </div>
            </div>
        </div>
    );
}
