import axios from "axios";

/**
 * ✅ Spring 단일 진입점
 * - Spring이 FastAPI로 갈 요청까지 프록시해준다는 전제
 * - 개발/배포 모두에서 프론트는 /api만 호출
 */
export const api = axios.create({
    baseURL: "/api",
    withCredentials: true, // 세션/쿠키 쓰면 유지(아니면 false로 꺼도 됨)
    timeout: 20000,
});

/* ------------------------------------------------------------------ */
/* Types (공통 모델은 여기서만 유지) */
/* ------------------------------------------------------------------ */

export interface Ingredient {
    name: string;
    amount: string;
    unit: string;
    note?: string;
}

export interface Step {
    step_number: number;
    instruction: string;
    timestamp: number;
    duration?: string;
    tips?: string;
}

export interface Recipe {
    title: string;
    description?: string;
    servings?: string;
    total_time?: string;
    difficulty?: string;
    ingredients: Ingredient[];
    steps: Step[];
    tips?: string[];
}

export interface Frame {
    step_number: number;
    timestamp: number;
    frame_path?: string;
    frame_filename: string;
}

export interface VideoInfo {
    video_id: string;
    title: string;
    duration: number;
    url: string;
}

export interface AnalysisResult {
    recipe: Recipe;
    frames: Frame[];
    video_info: VideoInfo;
    transcript: {
        full_text: string;
        segments: Array<{ start: number; end: number; text: string }>;
    };
}

/* ------------------------------------------------------------------ */
/* 1) Analysis (Spring -> FastAPI proxy) */
/* ------------------------------------------------------------------ */

export interface AnalyzeResponse {
    job_id: string;
    message: string;
}

export interface JobStatus {
    job_id: string;
    status: "pending" | "processing" | "completed" | "failed";
    progress: number;
    message: string;
    video_id?: string;
}

// ✅ Spring이 /api/analyze, /api/status/:jobId ... 이런 식으로 제공한다는 전제
export const analyzeVideo = async (url: string): Promise<AnalyzeResponse> => {
    const { data } = await api.post("/analyze", { url });
    return data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
    const { data } = await api.get(`/status/${jobId}`);
    return data;
};

export const getResult = async (jobId: string): Promise<AnalysisResult> => {
    const { data } = await api.get(`/result/${jobId}`);
    return data;
};

export const getFrameUrl = (jobId: string, filename: string): string => {
    return `/api/frames/${jobId}/${filename}`;
};

export const downloadExport = async (
    jobId: string,
    format: "markdown" | "pdf"
): Promise<Blob> => {
    const res = await api.get(`/export/${jobId}`, {
        params: { format },
        responseType: "blob",
    });
    return res.data;
};

/* ------------------------------------------------------------------ */
/* 2) Auth (간단 로그인/회원가입) */
/* ------------------------------------------------------------------ */

export type LoginReq = { username: string; password: string };
export type SignupReq = { username: string; password: string; nickname?: string };

export const loginApi = async (payload: LoginReq) => {
    const { data } = await api.post("/auth/login", payload);
    return data;
};

export const signupApi = async (payload: SignupReq) => {
    const { data } = await api.post("/auth/signup", payload);
    return data;
};

export const meApi = async () => {
    const { data } = await api.get("/auth/me");
    return data;
};

export const logoutApi = async () => {
    const { data } = await api.post("/auth/logout");
    return data;
};

/* ------------------------------------------------------------------ */
/* 3) Recipe 저장/불러오기 (Spring DB) */
/* ------------------------------------------------------------------ */
/**
 * 너가 기존에 /spring-api/recipe, /ingredient, /recipe-step, /recipes 로 쓰던 걸
 * Spring 쪽에서 /api/recipe... 로 맞춘다는 전제.
 * (경로가 다르면 여기만 바꾸면 됨)
 */

export interface RecipeSavePayload {
    title: string;
    description?: string;
    servings?: string;
    total_time?: string;
    difficulty?: string;
    ingredients: Ingredient[];
    steps: Step[];
    tips?: string[];
    // 필요하면 job_id, video_id, frames 등도 확장 가능
}

export const saveRecipe = async (recipeData: RecipeSavePayload) => {
    const { data } = await api.post("/recipe", recipeData);
    return data;
};

export const fetchRecipes = async () => {
    const { data } = await api.get("/recipes");
    return data;
};
