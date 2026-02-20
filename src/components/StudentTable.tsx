"use client";

import React, { useEffect, useState } from "react";
import EmotionBadge from "./EmotionBadge";
import { predictRisk } from "@/lib/api";
import type { StudentRecord } from "@/lib/mockData";

interface StudentTableProps {
  students: StudentRecord[];
}

const riskConfig: Record<
  string,
  { color: string; bg: string; emoji: string }
> = {
  High: { color: "text-[#FF4B4B]", bg: "bg-[#FFF0F0]", emoji: "🔴" },
  Medium: { color: "text-[#FFC800]", bg: "bg-[#FFF8E1]", emoji: "🟡" },
  Low: { color: "text-[#58CC02]", bg: "bg-[#F0FFF0]", emoji: "🟢" },
};

function getRiskLevel(score: number) {
  if (score >= 3.5) return "High";
  if (score >= 1.8) return "Medium";
  return "Low";
}

export default function StudentTable({ students }: StudentTableProps) {
  const [riskScores, setRiskScores] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRisks() {
      const newRiskMap: Record<string, number> = {};

      for (const student of students) {
        try {
          const result = await predictRisk(student);
          newRiskMap[student.id] = result.risk_score;
        } catch (error) {
          console.error("Prediction error:", error);
          newRiskMap[student.id] = 0;
        }
      }

      setRiskScores(newRiskMap);
      setLoading(false);
    }

    if (students.length > 0) {
      fetchRisks();
    }
  }, [students]);

  return (
    <div className="bg-white rounded-2xl border-2 border-[#E5E5E5] border-b-4 overflow-hidden">
      <div className="px-6 py-5 border-b-2 border-[#E5E5E5]">
        <h3 className="text-lg font-extrabold text-[#3C3C3C]">
          👥 Student Overview
        </h3>
        <p className="text-sm font-bold text-[#AFAFAF] mt-0.5">
          {students.length} students enrolled
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-[#F7F7F7] border-b-2 border-[#E5E5E5]">
              <th className="px-6 py-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">
                Name
              </th>
              <th className="px-6 py-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">
                Exam
              </th>
              <th className="px-6 py-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">
                Current Emotion
              </th>
              <th className="px-6 py-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">
                Risk Level
              </th>
              <th className="px-6 py-3 text-left text-[10px] font-extrabold text-[#AFAFAF] uppercase tracking-widest">
                Last Active
              </th>
            </tr>
          </thead>

          <tbody className="divide-y-2 divide-[#E5E5E5]">
            {students.map((student) => {
              const score = riskScores[student.id];
              const level =
                score !== undefined ? getRiskLevel(score) : "Low";

              return (
                <tr
                  key={student.id}
                  className="hover:bg-[#F7F7F7] transition-colors"
                >
                  {/* Name */}
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-[#DDF4FF] flex items-center justify-center border-2 border-[#1CB0F6]">
                        <span className="text-xs font-extrabold text-[#1CB0F6]">
                          {student.name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")}
                        </span>
                      </div>
                      <span className="font-extrabold text-[#3C3C3C]">
                        {student.name}
                      </span>
                    </div>
                  </td>

                  {/* Exam */}
                  <td className="px-6 py-4">
                    <span className="font-bold text-[#3C3C3C] bg-[#F7F7F7] px-3 py-1 rounded-lg border-2 border-[#E5E5E5]">
                      {student.exam}
                    </span>
                  </td>

                  {/* Emotion */}
                  <td className="px-6 py-4">
                    <EmotionBadge emotion={student.emotion} />
                  </td>

                  {/* Risk */}
                  <td className="px-6 py-4">
                    {loading || score === undefined ? (
                      <span className="text-xs font-bold text-gray-400">
                        Calculating...
                      </span>
                    ) : (
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-extrabold ${riskConfig[level].color} ${riskConfig[level].bg}`}
                      >
                        {riskConfig[level].emoji} {level} (
                        {score.toFixed(2)})
                      </span>
                    )}
                  </td>

                  {/* Last Active */}
                  <td className="px-6 py-4 text-[#AFAFAF] font-bold">
                    {student.lastActive}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}