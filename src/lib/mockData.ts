// ─── Types ───────────────────────────────────────────────
export type Emotion = "Stressed" | "Focused" | "Confused" | "Calm";
export type RiskLevel = "High" | "Medium" | "Low";

export interface StudentProfile {
    name: string;
    initials: string;
    exam: string;
    streak: number;
    email: string;
}

export interface MetricItem {
    label: string;
    value: string;
    subtext?: string;
    icon: string;
}

export interface RecentSession {
    id: string;
    topic: string;
    date: string;
    duration: string;
    emotion: Emotion;
    score: number;
}

export interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: string;
}

export interface StudentRecord {
    id: string;
    name: string;
    exam: string;
    emotion: Emotion;
    riskLevel: RiskLevel;
    lastActive: string;
}

// ─── Student Profile ─────────────────────────────────────
export const mockStudentProfile: StudentProfile = {
    name: "Rishi Verma",
    initials: "RV",
    exam: "GRE",
    streak: 14,
    email: "rishi@example.com",
};

// ─── Student Metrics ─────────────────────────────────────
export const mockStudentMetrics: MetricItem[] = [
    { label: "Current Emotion", value: "Focused", subtext: "Based on last session", icon: "😊" },
    { label: "Study Streak", value: "14 days", subtext: "+2 from last week", icon: "🔥" },
    { label: "Weak Topics", value: "3 topics", subtext: "Algebra, Geometry, RC", icon: "📌" },
    { label: "Engagement Score", value: "87%", subtext: "Above average", icon: "📈" },
];

// ─── Recent Sessions ─────────────────────────────────────
export const mockRecentSessions: RecentSession[] = [
    { id: "s1", topic: "Algebra — Quadratics", date: "Feb 19, 2026", duration: "42 min", emotion: "Focused", score: 88 },
    { id: "s2", topic: "Reading Comprehension", date: "Feb 18, 2026", duration: "35 min", emotion: "Confused", score: 62 },
    { id: "s3", topic: "Geometry — Circles", date: "Feb 17, 2026", duration: "50 min", emotion: "Stressed", score: 55 },
    { id: "s4", topic: "Vocabulary Building", date: "Feb 16, 2026", duration: "28 min", emotion: "Calm", score: 74 },
    { id: "s5", topic: "Data Interpretation", date: "Feb 15, 2026", duration: "38 min", emotion: "Stressed", score: 69 },
];

// ─── Initial Chat Messages ───────────────────────────────
export const mockChatMessages: ChatMessage[] = [
    {
        id: "m1",
        role: "assistant",
        content: "Welcome to your study session! I'll adapt to your pace and emotional state. What topic would you like to focus on today?",
        timestamp: "12:00 PM",
    },
    {
        id: "m2",
        role: "user",
        content: "Let's work on quadratic equations. I had trouble with them last time.",
        timestamp: "12:01 PM",
    },
    {
        id: "m3",
        role: "assistant",
        content: "Great choice! Let's start with the basics and build up. A quadratic equation has the form ax² + bx + c = 0. Can you tell me what the quadratic formula is?",
        timestamp: "12:01 PM",
    },
];

// ─── Teacher Metrics ─────────────────────────────────────
export const mockTeacherMetrics: MetricItem[] = [
    { label: "Total Students", value: "128", subtext: "+12 this month", icon: "👥" },
    { label: "High Risk Students", value: "8", subtext: "Needs attention", icon: "⚠️" },
    { label: "Avg Emotion Stability", value: "72%", subtext: "Stable trend", icon: "📊" },
    { label: "Active Sessions", value: "23", subtext: "Currently live", icon: "🟢" },
];

// ─── Student Records (Teacher Table) ─────────────────────
export const mockStudents: StudentRecord[] = [
    { id: "st1", name: "Aarav Patel", exam: "GRE", emotion: "Focused", riskLevel: "Low", lastActive: "2 min ago" },
    { id: "st2", name: "Meera Singh", exam: "GMAT", emotion: "Stressed", riskLevel: "High", lastActive: "15 min ago" },
    { id: "st3", name: "Rohan Gupta", exam: "CAT", emotion: "Stressed", riskLevel: "High", lastActive: "1 hr ago" },
    { id: "st4", name: "Priya Sharma", exam: "GRE", emotion: "Calm", riskLevel: "Medium", lastActive: "30 min ago" },
    { id: "st5", name: "Arjun Reddy", exam: "GMAT", emotion: "Confused", riskLevel: "Medium", lastActive: "45 min ago" },
    { id: "st6", name: "Kavya Nair", exam: "CAT", emotion: "Focused", riskLevel: "Low", lastActive: "5 min ago" },
    { id: "st7", name: "Ishaan Joshi", exam: "GRE", emotion: "Stressed", riskLevel: "High", lastActive: "20 min ago" },
    { id: "st8", name: "Diya Menon", exam: "GMAT", emotion: "Calm", riskLevel: "Low", lastActive: "10 min ago" },
];

// ─── Exam Options ────────────────────────────────────────
export const examOptions = ["GRE", "GMAT", "CAT", "SAT", "UPSC"];
