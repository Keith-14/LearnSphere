// ─── Types ───────────────────────────────────────────────
export type Emotion = "Stressed" | "Focused" | "Confused" | "Calm";
export type RiskLevel = "High" | "Medium" | "Low";

export interface StudentProfile {
    name: string;
    initials: string;
    exam: string;
    streak: number;
    email: string;
    avatar?: string;
}

export interface QuizQuestion {
    id: string;
    question: string;
    options: string[];
    correctIndex: number;
    topic: string;
}

// ─── Pingo Avatars ───────────────────────────────────────
export const pingoAvatars: Record<Emotion, string> = {
    Stressed: "/pingo_angry.png",
    Focused: "/pingo_confident.png",
    Confused: "/pingo_thinking.png",
    Calm: "/pingo_happy.png",
};

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
    { id: "s1", topic: "Quant — Probability & Venn", date: "Feb 19, 2026", duration: "42 min", emotion: "Focused", score: 88 },
    { id: "s2", topic: "Verbal — Reading Comp", date: "Feb 18, 2026", duration: "35 min", emotion: "Confused", score: 62 },
    { id: "s3", topic: "Physics — Fluid Mechanics", date: "Feb 17, 2026", duration: "50 min", emotion: "Stressed", score: 55 },
    { id: "s4", topic: "CAT — Logical Reasoning", date: "Feb 16, 2026", duration: "28 min", emotion: "Calm", score: 74 },
    { id: "s5", topic: "JEE — Organic Chemistry", date: "Feb 15, 2026", duration: "38 min", emotion: "Focused", score: 69 },
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

// ─── Quiz Questions ──────────────────────────────────────
export const mockQuizQuestions: QuizQuestion[] = [
    {
        id: "q1",
        question: "What is the discriminant of the quadratic equation 2x² + 5x - 3 = 0?",
        options: ["49", "37", "25", "31"],
        correctIndex: 0,
        topic: "Algebra",
    },
    {
        id: "q2",
        question: "If f(x) = 3x² - 12x + 7, what is the vertex of the parabola?",
        options: ["(2, 5)", "(2, -5)", "(-2, -5)", "(4, 7)"],
        correctIndex: 1,
        topic: "Algebra",
    },
    {
        id: "q3",
        question: "A circle has a radius of 7 cm. What is its area?",
        options: ["154 cm²", "44 cm²", "49π cm²", "Both A and C"],
        correctIndex: 3,
        topic: "Geometry",
    },
    {
        id: "q4",
        question: "Which word best completes: 'The speaker's _____ remarks offended the audience.'",
        options: ["Eloquent", "Acerbic", "Benign", "Tepid"],
        correctIndex: 1,
        topic: "Vocabulary",
    },
    {
        id: "q5",
        question: "What is the sum of all integers from 1 to 50?",
        options: ["1225", "1275", "1250", "1300"],
        correctIndex: 1,
        topic: "Data Interpretation",
    },
];

export const examQuestions: Record<string, QuizQuestion[]> = {
    GRE: [
        ...mockQuizQuestions,
        { id: "g6", question: "What is the value of 5! (5 factorial)?", options: ["100", "120", "60", "24"], correctIndex: 1, topic: "Math" },
        { id: "g7", question: "Select the synonym for 'Ephemeral'", options: ["Short-lived", "Eternal", "Beautiful", "Strong"], correctIndex: 0, topic: "Verbal" },
        { id: "g8", question: "If x + y = 10 and x - y = 2, what is x?", options: ["4", "6", "8", "5"], correctIndex: 1, topic: "Algebra" },
        { id: "g9", question: "What is the sum of interior angles of a pentagon?", options: ["360°", "540°", "180°", "720°"], correctIndex: 1, topic: "Geometry" },
        { id: "g10", question: "If a car travels 60 miles in 1 hour, how far does it travel in 15 minutes?", options: ["10 miles", "20 miles", "15 miles", "5 miles"], correctIndex: 2, topic: "Math" }
    ],
    JEE: [
        { id: "j1", question: "The value of lim (x->0) (sin x / x) is:", options: ["0", "1", "inf", "undefined"], correctIndex: 1, topic: "Calculus" },
        { id: "j2", question: "What is the derivative of e^(x^2)?", options: ["e^(x^2)", "2x * e^(x^2)", "2 * e^(x^2)", "x^2 * e^x"], correctIndex: 1, topic: "Calculus" },
        { id: "j3", question: "The escape velocity on earth is approximately:", options: ["9.8 km/s", "11.2 km/s", "11.2 m/s", "42 km/s"], correctIndex: 1, topic: "Physics" },
        { id: "j4", question: "Which lens is used to correct Myopia?", options: ["Concave", "Convex", "Cylindrical", "None"], correctIndex: 0, topic: "Physics" },
        { id: "j5", question: "What is the hybridisation of Carbon in Methane?", options: ["sp3", "sp2", "sp", "dsp2"], correctIndex: 0, topic: "Chemistry" },
        { id: "j6", question: "Avogadro constant is roughly:", options: ["6.626 x 10^-34", "6.022 x 10^23", "1.6 x 10^-19", "3 x 10^8"], correctIndex: 1, topic: "Chemistry" },
        { id: "j7", question: "The integration of 1/x dx is:", options: ["x^2", "ln|x|", "-1/x^2", "e^x"], correctIndex: 1, topic: "Math" },
        { id: "j8", question: "Power is defined as:", options: ["Force * Time", "Work / Time", "Energy * Distance", "Work * Time"], correctIndex: 1, topic: "Physics" },
        { id: "j9", question: "Noble gases are in which group?", options: ["17", "18", "1", "2"], correctIndex: 1, topic: "Chemistry" },
        { id: "j10", question: "The first law of thermodynamics is a statement of:", options: ["Entropy", "Conservation of Energy", "Conservation of Mass", "Heat transfer"], correctIndex: 1, topic: "Physics" }
    ],
    GMAT: [
        { id: "gm1", question: "If the ratio of A:B is 3:4 and B:C is 5:6, what is A:C?", options: ["15:24", "5:8", "1:2", "3:6"], correctIndex: 1, topic: "Quant" },
        { id: "gm2", question: "Critical Reasoning: Which strengthen the argument?", options: ["Alternative theory", "Evidence supporting premise", "Counter example", "Statistical bias"], correctIndex: 1, topic: "Verbal" },
        { id: "gm3", question: "Data Sufficiency: Is x > 0? (1) x^2 = 4 (2) x^3 = 8", options: ["(1) alone is sufficient", "(2) alone is sufficient", "Both together", "Neither"], correctIndex: 1, topic: "Quant" },
        { id: "gm4", question: "What is 15% of 200?", options: ["20", "30", "15", "45"], correctIndex: 1, topic: "Quant" },
        { id: "gm5", question: "Identify the grammatical error in the sentence.", options: ["Tense", "Subject-Verb agreement", "Diction", "None"], correctIndex: 1, topic: "Verbal" },
        { id: "gm6", question: "A shopkeeper sells at 20% profit. If cost is $100, what is selling price?", options: ["$80", "$120", "$100", "$140"], correctIndex: 1, topic: "Quant" },
        { id: "gm7", question: "Find the odd one out.", options: ["Circle", "Square", "Rectangle", "Cube"], correctIndex: 3, topic: "Reasoning" },
        { id: "gm8", question: "If x + 5 = 12, then 2x = ?", options: ["7", "14", "24", "10"], correctIndex: 1, topic: "Quant" },
        { id: "gm9", question: "The average of 10, 20, 30 is:", options: ["15", "20", "25", "30"], correctIndex: 1, topic: "Quant" },
        { id: "gm10", question: "Reading Comprehension focuses on:", options: ["Speed only", "Inference", "Handwriting", "Spelling"], correctIndex: 1, topic: "Verbal" }
    ],
    CAT: [
        { id: "c1", question: "Number System: How many zeros at the end of 100!?", options: ["20", "24", "25", "26"], correctIndex: 1, topic: "Quant" },
        { id: "c2", question: "Logical Reasoning: Sitting arrangement in a circle...", options: ["Option B", "Option A", "Option C", "Option D"], correctIndex: 1, topic: "LR" },
        { id: "c3", question: "What is 2^10?", options: ["512", "1024", "2048", "1000"], correctIndex: 1, topic: "Quant" },
        { id: "c4", question: "Data Interpretation: Total revenue in Q3 vs Q4...", options: ["5% decrease", "10% increase", "Stayed same", "Double"], correctIndex: 1, topic: "DI" },
        { id: "c5", question: "The root of 144 is:", options: ["14", "12", "16", "10"], correctIndex: 1, topic: "Quant" },
        { id: "c6", question: "Choose the correct spelling:", options: ["Enterprenuer", "Entrepreneur", "Entreperneur", "Entreprenure"], correctIndex: 1, topic: "VARC" },
        { id: "c7", question: "If a work is done by A in 10 days and B in 20, together they take:", options: ["15 days", "6.67 days", "5 days", "10 days"], correctIndex: 1, topic: "Quant" },
        { id: "c8", question: "Identify the idiom meaning 'to be happy'.", options: ["Under the weather", "Over the moon", "Barking up wrong tree", "Beat around the bush"], correctIndex: 1, topic: "VARC" },
        { id: "c9", question: "Find next in series: 2, 4, 8, 16, ...", options: ["24", "32", "20", "64"], correctIndex: 1, topic: "LR" },
        { id: "c10", question: "What is the probability of rolling a 6 on a die?", options: ["1/2", "1/6", "1/3", "1/5"], correctIndex: 1, topic: "Quant" }
    ],
    SAT: [
        { id: "s1", question: "Passage analysis: The author's tone is...", options: ["Cynical", "Nostalgic", "Optimistic", "Indifferent"], correctIndex: 1, topic: "Reading" },
        { id: "s2", question: "Solve for x: 3x - 5 = 16", options: ["6", "7", "9", "5"], correctIndex: 1, topic: "Math" },
        { id: "s3", question: "Which is a prime number?", options: ["15", "17", "21", "27"], correctIndex: 1, topic: "Math" },
        { id: "s4", question: "Grammar: Choose the correct pronoun.", options: ["Who", "Whom", "Whose", "Which"], correctIndex: 1, topic: "Writing" },
        { id: "s5", question: "What is the value of 0.25 as a fraction?", options: ["1/2", "1/4", "1/5", "1/10"], correctIndex: 1, topic: "Math" },
        { id: "s6", question: "Triangles: The sum of angles is:", options: ["360°", "180°", "90°", "270°"], correctIndex: 1, topic: "Math" },
        { id: "s7", question: "Vocabulary: 'Benevolent' means:", options: ["Cruel", "Kind", "Large", "Hidden"], correctIndex: 1, topic: "Verbal" },
        { id: "s8", question: "If 10% of x is 5, what is x?", options: ["5", "50", "100", "10"], correctIndex: 1, topic: "Math" },
        { id: "s9", question: "Identify the main idea of the paragraph.", options: ["Option B", "Option A", "Option C", "Option D"], correctIndex: 1, topic: "Reading" },
        { id: "s10", question: "What is 4 squared?", options: ["8", "16", "12", "20"], correctIndex: 1, topic: "Math" }
    ]
};

// ─── Exam Options ────────────────────────────────────────
export const examOptions = ["GRE", "GMAT", "CAT", "SAT", "UPSC"];
