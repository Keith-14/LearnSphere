"use client";

import React from "react";

interface DashboardCardProps {
    children: React.ReactNode;
    className?: string;
}

export default function DashboardCard({ children, className = "" }: DashboardCardProps) {
    return (
        <div
            className={`bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 p-6 ${className}`}
        >
            {children}
        </div>
    );
}
