export async function predictRisk(student: any) {
  try {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        avg_score: student.avgScore,
        stress_level: student.stressLevel,
        confidence_level: student.confidenceLevel,
        login_count: student.loginCount,
        avg_session_time: student.avgSessionTime,
      }),
    });

    if (!response.ok) {
      throw new Error(`Prediction failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  } catch (error) {
    console.error("Fetch error details:", error);
    throw error;
  }
}