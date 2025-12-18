import axios from "axios";

/**
 * ✅ Spring 단일 진입점
 * - Spring이 FastAPI로 갈 요청까지 프록시해준다는 전제
 * - 개발/배포 모두에서 프론트는 /api만 호출
 */
export const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL + "/api",
    timeout: 20000,
});

/* ------------------------------------------------------------------ */
/* Types (공통 모델은 여기서만 유지) */
/* ------------------------------------------------------------------ */

api.interceptors.request.use((config) => {
    const email = localStorage.getItem("login_email");

    if (email && config.headers) {
        config.headers.set("email", email);
    }

    return config;
});

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
    jobId: string;
    message: string;
}

export interface JobStatus {
    jobId: string;
    status: "pending" | "processing" | "completed" | "failed";
    progress: number;
    message: string;
    video_id?: string;
}

// ✅ Spring이 /api/analyze, /api/status/:jobId ... 이런 식으로 제공한다는 전제
export const analyzeVideo = async (url: string): Promise<AnalyzeResponse> => {
    const { data } = await api.post("/recipes/analyze", { url });
    return data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
    const { data } = await api.get(`/recipes/status/${jobId}`);
    return data;
};

export const getResult = async (jobId: string): Promise<AnalysisResult> => {
    const { data } = await api.get(`/recipes/result/${jobId}`);
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

export type LoginReq = { email: string; password: string };
export type SignupReq = { email: string; password: string; nickname?: string };

export const loginApi = async (payload: LoginReq) => {
    const { data } = await api.post("/auth/login", payload);
    console.log(data);
    return data;
};

export const signupApi = async (payload: SignupReq) => {
    const { data } = await api.post("/user/signup", payload);
    console.log(data);
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
    // 필요하면 jobId, video_id, frames 등도 확장 가능
}

export const saveRecipe = async (recipeData: RecipeSavePayload) => {
    const { data } = await api.post("/recipe", recipeData);
    return data;
};

export const fetchRecipes = async () => {
    const { data } = await api.get("/recipes");
    return data;
};

// SSE
export type ProgressPayload = {
    jobId?: string;
    status?: "pending" | "processing" | "completed" | "failed" | string;
    progress?: number;
    message?: string;
    videoId?: string;
}

export function subscribe(
    jobId: string,
    handlers: {
        onConnected?: (data: any) => void;
        onProgress?: (data: ProgressPayload) => void;
        onCompleted?: (data?: any) => void;
        onFailed?: (data?: any) => void;
        onError?: (e: any) => void;
    }
) {
    const es = new EventSource(`http://localhost:8080/api/sse/jobs/${jobId}`);
    const safeJson = (e: MessageEvent) => {
        try {
            return JSON.parse(e.data);
        } catch { return e.data; }
    }

    es.addEventListener("connected", (e) => handlers.onConnected?.(safeJson(e)));

    es.addEventListener("progress", (e) => handlers.onProgress?.(safeJson(e)));

    es.addEventListener("completed", (e) => {
        handlers.onCompleted?.(safeJson(e as MessageEvent));
        es.close();
    });

    es.addEventListener("failed", (e) => {
        handlers.onFailed?.(safeJson(e as MessageEvent));
        es.close();
    });

    es.addEventListener("error", (e) => handlers.onError?.(e));
    es.onerror = (e) => {
        es.close();
    };

    return () => es.close();
}