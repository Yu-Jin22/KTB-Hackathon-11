import React, { useState, useRef, useEffect, useLayoutEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    stepNumber?: number;
    imageUrl?: string;
}

interface Step {
    step_number: number;
    instruction: string;
    tips?: string;
    timestamp?: number;
}

interface Recipe {
    title: string;
    description?: string;
    difficulty?: string;
    total_time?: string;
    servings?: string;
    ingredients: Array<{ name: string; amount: string; unit: string; note?: string }>;
    steps: Step[];
    tips?: string[];
}

const API_BASE = import.meta.env.VITE_API_BASE_URL + "/api/chat";
const PRESIGNED_API_BASE = import.meta.env.VITE_API_BASE_URL + "/api/presigned-url";

const getAuthHeaders = () => {
    const email = localStorage.getItem("login_email");
    return {
        "Content-Type": "application/json",
        ...(email ? { email } : {})
    };
};

type CookingStatus = 'cooking' | 'finished';

export default function ChatRoom() {
    const location = useLocation();
    const navigate = useNavigate();
    const recipe: Recipe | null = location.state?.recipe || null;

    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentStep, setCurrentStep] = useState(1);
    const [completedSteps, setCompletedSteps] = useState<number[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showStepPanel, setShowStepPanel] = useState(false);
    const [cookingStatus, setCookingStatus] = useState<CookingStatus>('cooking');

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // ✅ IME(한글) 조합 상태
    const isComposingRef = useRef(false);

    // ✅ 스크롤 제어
    const isNearBottomRef = useRef(true);
    const forceScrollRef = useRef(false);

    // ✅ 페이지네이션(과거메시지)
    const PAGE_SIZE = 5;
    const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
    const messagesBoxRef = useRef<HTMLDivElement>(null);
    const restoreScrollRef = useRef<{ prevHeight: number } | null>(null);

    // -------- helpers --------
    const makeId = () =>
        (typeof crypto !== "undefined" && "randomUUID" in crypto)
            ? crypto.randomUUID()
            : `${Date.now()}-${Math.random().toString(16).slice(2)}`;

    const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
        const el = messagesBoxRef.current;
        if (!el) return;

        // DOM 반영 2프레임 보장
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const top = Math.max(0, el.scrollHeight - el.clientHeight);
                el.scrollTo({ top, behavior });
            });
        });
    };

    // -------- session start --------
    useEffect(() => {
        if (recipe && !sessionId) startSession();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [recipe]);

    const startSession = async () => {
        if (!recipe) return;

        try {
            const response = await fetch(`${API_BASE}/start`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({ recipe })
            });

            const data = await response.json();
            setSessionId(data.session_id);

            setMessages([{
                id: makeId(),
                role: 'assistant',
                content: `안녕! 오늘 **${recipe.title}** 만들어볼 거야 🍳\n\n총 ${recipe.steps.length}단계로 진행할게. 준비되면 **Step 1**부터 시작하자!\n\n궁금한 거 있으면 언제든 물어봐. 사진 찍어서 보여주면 피드백도 해줄게! 📸`
            }]);

            // 첫 메시지는 아래로
            forceScrollRef.current = true;
        } catch (error) {
            console.error('세션 시작 실패:', error);
        }
    };

    // -------- scroll tracking --------
    useEffect(() => {
        const el = messagesBoxRef.current;
        if (!el) return;

        const onScroll = () => {
            const distance = el.scrollHeight - (el.scrollTop + el.clientHeight);
            isNearBottomRef.current = distance < 120;
        };

        el.addEventListener("scroll", onScroll, { passive: true });
        return () => el.removeEventListener("scroll", onScroll);
    }, []);

    // 과거 메시지 로드 시 스크롤 유지
    useLayoutEffect(() => {
        const el = messagesBoxRef.current;
        const ctx = restoreScrollRef.current;
        if (!el || !ctx) return;

        const nextHeight = el.scrollHeight;
        el.scrollTop = nextHeight - ctx.prevHeight + el.scrollTop;

        restoreScrollRef.current = null;
    }, [visibleCount]);

    // ✅ 스크롤은 여기서만!
    useLayoutEffect(() => {
        if (!messagesBoxRef.current) return;

        if (forceScrollRef.current) {
            scrollToBottom("smooth");
            forceScrollRef.current = false;
            return;
        }

        if (isNearBottomRef.current) {
            scrollToBottom("smooth");
        }
    }, [messages.length]);

    const handleScroll = () => {
        const el = messagesBoxRef.current;
        if (!el) return;

        if (el.scrollTop < 30) {
            restoreScrollRef.current = { prevHeight: el.scrollHeight };
            setVisibleCount((v) => Math.min(messages.length, v + PAGE_SIZE));
        }
    };

    // -------- panel behavior --------
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") setShowStepPanel(false);
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, []);

    // (선택) 패널 열렸을 때 바디 스크롤 잠금(모바일)
    useEffect(() => {
        if (!showStepPanel) return;
        const prev = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => { document.body.style.overflow = prev; };
    }, [showStepPanel]);

    // -------- image upload --------
    const uploadImageToS3 = async (file: File): Promise<string> => {
        const presignedRes = await fetch(PRESIGNED_API_BASE, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fileName: file.name, contentType: file.type })
        });

        if (!presignedRes.ok) throw new Error("Presigned URL 발급 실패");

        const { uploadUrl, fileUrl } = await presignedRes.json();

        const uploadRes = await fetch(uploadUrl, {
            method: "PUT",
            headers: { "Content-Type": file.type },
            body: file
        });

        if (!uploadRes.ok) throw new Error("S3 업로드 실패");

        return fileUrl;
    };

    const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setSelectedImage(file);
        const reader = new FileReader();
        reader.onloadend = () => setImagePreview(reader.result as string);
        reader.readAsDataURL(file);
    };

    const removeImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    // -------- actions --------
    const sendMessage = async () => {
        if (!inputText.trim() && !selectedImage) return;
        if (!sessionId) return;

        const userMessage: Message = {
            id: makeId(),
            role: 'user',
            content: inputText,
            stepNumber: currentStep,
            imageUrl: imagePreview || undefined
        };

        // ✅ 사용자가 위에 있어도 "전송"하면 무조건 아래로
        forceScrollRef.current = true;
        isNearBottomRef.current = true;

        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsLoading(true);

        try {
            let imageUrl: string | null = null;
            if (selectedImage) imageUrl = await uploadImageToS3(selectedImage);

            const response = await fetch(`${API_BASE}/message`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    session_id: sessionId,
                    step_number: currentStep,
                    message: inputText || '이 사진 봐줘',
                    image_url: imageUrl
                })
            });

            const data = await response.json();

            // ✅ 응답 와도 아래로
            forceScrollRef.current = true;
            isNearBottomRef.current = true;

            setMessages(prev => [...prev, {
                id: makeId(),
                role: 'assistant',
                content: data.reply,
                stepNumber: currentStep
            }]);

            if (data.session_status) {
                setCompletedSteps(data.session_status.completed_steps || []);
            }
        } catch (error) {
            console.error('메시지 전송 실패:', error);

            forceScrollRef.current = true;
            isNearBottomRef.current = true;

            setMessages(prev => [...prev, {
                id: makeId(),
                role: 'assistant',
                content: '앗, 오류가 발생했어. 다시 시도해줄래?'
            }]);
        } finally {
            setIsLoading(false);
            removeImage();
        }
    };

    const completeCurrentStep = async () => {
        if (!sessionId) return;

        try {
            const response = await fetch(`${API_BASE}/session/${sessionId}/complete-step/${currentStep}`, {
                method: 'POST',
                headers: getAuthHeaders(),
            });

            const data = await response.json();
            setCompletedSteps(prev => [...prev, currentStep]);

            forceScrollRef.current = true;
            isNearBottomRef.current = true;

            if (data.is_finished) {
                setCookingStatus('finished');
                setMessages(prev => [...prev, {
                    id: makeId(),
                    role: 'assistant',
                    content: `🎉 **축하해! ${recipe?.title} 완성!**\n\n정말 잘했어! 맛있게 먹어 🍽️\n\n오늘 요리 어땠어?`
                }]);
            } else {
                setCurrentStep(data.next_step);
                const nextStepInfo = recipe?.steps[data.next_step - 1];
                setMessages(prev => [...prev, {
                    id: makeId(),
                    role: 'assistant',
                    content: `✅ **Step ${currentStep} 완료!**\n\n다음은 **Step ${data.next_step}**이야:\n> ${nextStepInfo?.instruction}\n\n${nextStepInfo?.tips ? `💡 팁: ${nextStepInfo.tips}` : ''}\n\n준비되면 시작해!`
                }]);
            }
        } catch (error) {
            console.error('단계 완료 실패:', error);
        }
    };

    const selectStep = (stepNum: number) => {
        setCurrentStep(stepNum);
        setShowStepPanel(false); // ✅ 모바일에서 선택하면 닫기

        const stepInfo = recipe?.steps[stepNum - 1];

        forceScrollRef.current = true;
        isNearBottomRef.current = true;

        setMessages(prev => [...prev, {
            id: makeId(),
            role: 'assistant',
            content: `📍 **Step ${stepNum}**로 이동했어!\n\n> ${stepInfo?.instruction}\n\n${stepInfo?.tips ? `💡 팁: ${stepInfo.tips}` : ''}\n\n질문 있으면 말해줘!`
        }]);
    };

    // -------- guards --------
    if (!recipe) {
        return (
            <div className="h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-lg mb-4">레시피 정보가 없습니다.</p>
                    <button
                        onClick={() => navigate('/')}
                        className="px-4 py-2 gradient-bg rounded-full font-bold"
                    >
                        홈으로 돌아가기
                    </button>
                </div>
            </div>
        );
    }

    const progress = recipe.steps.length > 0
        ? Math.round((completedSteps.length / recipe.steps.length) * 100)
        : 0;

    const visibleMessages = messages.slice(Math.max(0, messages.length - visibleCount));

    return (
        <div className="h-dvh flex flex-col bg-gray-50">
            {/* Header */}
            <header className="h-16 flex items-center justify-between px-3 sm:px-4 bg-white/80 backdrop-blur-sm border-b border-[var(--line)] sticky top-0 z-50">
                <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                    <button
                        onClick={() => navigate('/')}
                        className="p-2 hover:bg-gray-100 rounded-full shrink-0"
                        aria-label="뒤로가기"
                    >
                        ←
                    </button>

                    <div className="min-w-0">
                        <h1 className="font-black text-[13px] sm:text-sm truncate">{recipe.title}</h1>
                        <p className="text-[11px] sm:text-xs text-[var(--muted)]">
                            Step {currentStep} / {recipe.steps.length} · {progress}% 완료
                        </p>
                    </div>
                </div>

                {/* 단계보기: 아이콘 + 배지 */}
                <button
                    onClick={() => setShowStepPanel((v) => !v)}
                    className="
            group relative
            w-10 h-10
            grid place-items-center
            rounded-full
            bg-white/90
            border border-[var(--line)]
            shadow-[var(--shadow2)]
            hover:bg-white
            hover:shadow-[var(--shadow)]
            transition
            shrink-0
          "
                    aria-label={showStepPanel ? "단계 패널 닫기" : "단계 패널 열기"}
                    title={showStepPanel ? "단계 닫기" : "단계 보기"}
                >
                    <svg className="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path d="M8 6h13" stroke="rgba(23,34,51,.78)" strokeWidth="1.7" strokeLinecap="round" />
                        <path d="M8 12h13" stroke="rgba(23,34,51,.78)" strokeWidth="1.7" strokeLinecap="round" />
                        <path d="M8 18h13" stroke="rgba(23,34,51,.78)" strokeWidth="1.7" strokeLinecap="round" />
                        <path d="M4 6h.01" stroke="rgba(23,34,51,.78)" strokeWidth="3.2" strokeLinecap="round" />
                        <path d="M4 12h.01" stroke="rgba(23,34,51,.78)" strokeWidth="3.2" strokeLinecap="round" />
                        <path d="M4 18h.01" stroke="rgba(23,34,51,.78)" strokeWidth="3.2" strokeLinecap="round" />
                    </svg>

                    <span
                        className="
              absolute -right-1 -top-1
              min-w-[22px] h-[18px]
              px-1
              rounded-full
              text-[10px]
              font-black
              grid place-items-center
              border border-[var(--line)]
              bg-white
              text-[rgba(23,34,51,.86)]
              shadow-[var(--shadow2)]
            "
                    >
                        {progress}%
                    </span>

                    {showStepPanel && (
                        <span className="absolute -left-1 -bottom-1 w-3 h-3 rounded-full gradient-bg border border-[rgba(23,34,51,.08)]" />
                    )}
                </button>
            </header>

            <div className="flex-1 flex overflow-hidden relative">
                {/* ✅ Backdrop: 항상 렌더(애니메이션 위해) */}
                <div
                    onClick={() => setShowStepPanel(false)}
                    className={`
            fixed inset-0 z-40 lg:hidden bg-black/35
            transition-opacity duration-300
            ${showStepPanel ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"}
          `}
                />

                {/* ✅ Step Panel: 항상 렌더(애니메이션 위해) */}
                <aside
                    className={`
            fixed lg:static
            z-50 lg:z-auto
            inset-y-0 left-0
            w-[86vw] max-w-[340px] lg:w-72
            bg-white
            border-r border-[var(--line)]
            overflow-y-auto
            shadow-[0_20px_60px_rgba(0,0,0,.18)] lg:shadow-none
            transform transition-transform duration-300 ease-out
            ${showStepPanel ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
                >
                    {/* Mobile Panel Header */}
                    <div className="lg:hidden sticky top-0 z-10 bg-white border-b border-[var(--line)] px-4 py-3 flex items-center justify-between">
                        <div className="font-black text-sm">단계</div>
                        <button
                            onClick={() => setShowStepPanel(false)}
                            className="w-9 h-9 grid place-items-center rounded-full hover:bg-gray-100"
                            aria-label="닫기"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Progress */}
                    <div className="p-4 border-b border-[var(--line)]">
                        <div className="flex justify-between text-xs mb-2">
                            <span className="font-black">진행률</span>
                            <span className="font-black">{progress}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div className="h-full gradient-bg transition-all" style={{ width: `${progress}%` }} />
                        </div>
                    </div>

                    {/* Steps */}
                    <div className="p-2">
                        {recipe.steps.map((step, idx) => {
                            const stepNum = idx + 1;
                            const isCompleted = completedSteps.includes(stepNum);
                            const isCurrent = stepNum === currentStep;

                            return (
                                <button
                                    key={stepNum}
                                    onClick={() => selectStep(stepNum)}
                                    className={`w-full text-left p-3 rounded-xl mb-2 transition-all ${isCurrent
                                        ? 'gradient-bg-soft border-2 border-[rgba(69,197,138,.5)]'
                                        : isCompleted
                                            ? 'bg-green-50 border border-green-200'
                                            : 'bg-gray-50 hover:bg-gray-100 border border-transparent'
                                        }`}
                                >
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-black ${isCompleted
                                            ? 'bg-green-500 text-white'
                                            : isCurrent
                                                ? 'gradient-bg'
                                                : 'bg-gray-300'
                                            }`}>
                                            {isCompleted ? '✓' : stepNum}
                                        </span>
                                        <span className="font-black text-sm">Step {stepNum}</span>
                                        {isCurrent && <span className="text-xs">👈 현재</span>}
                                    </div>
                                    <p className="text-xs text-[var(--muted)] line-clamp-2 ml-8">
                                        {step.instruction}
                                    </p>
                                </button>
                            );
                        })}
                    </div>

                    {!completedSteps.includes(currentStep) && cookingStatus !== "finished" && (
                        <div className="p-4 border-t border-[var(--line)] sticky bottom-0 bg-white">
                            <button
                                onClick={completeCurrentStep}
                                className="w-full py-3 gradient-bg rounded-xl font-black text-sm hover:opacity-90 transition"
                            >
                                ✅ Step {currentStep} 완료!
                            </button>
                        </div>
                    )}
                </aside>

                {/* Chat Area */}
                <main className="flex-1 flex flex-col overflow-hidden">
                    {/* Messages */}
                    <div
                        ref={messagesBoxRef}
                        onScroll={() => {
                            handleScroll();
                            // 스크롤 핸들러에서 near-bottom도 최신화되도록 (안전)
                            const el = messagesBoxRef.current;
                            if (el) {
                                const distance = el.scrollHeight - (el.scrollTop + el.clientHeight);
                                isNearBottomRef.current = distance < 120;
                            }
                        }}
                        className="flex-1 overflow-y-auto p-3 sm:p-4"
                    >
                        {/* ✅ 아래부터 쌓이도록 */}
                        <div className="flex flex-col gap-3 sm:gap-4 min-h-full justify-end">
                            {visibleMessages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`
                      max-w-[92%] sm:max-w-[80%]
                      rounded-2xl p-3 sm:p-4
                      ${msg.role === 'user'
                                                ? 'bg-[var(--g-200)] rounded-br-sm'
                                                : 'bg-white border border-[var(--line)] rounded-bl-sm'}
                    `}
                                    >
                                        {msg.stepNumber && (
                                            <span className="text-[11px] sm:text-xs text-[var(--muted)] mb-1 block font-semibold">
                                                Step {msg.stepNumber}
                                            </span>
                                        )}

                                        {msg.imageUrl && (
                                            <img
                                                src={msg.imageUrl}
                                                alt="uploaded"
                                                className="max-w-full rounded-lg mb-2 max-h-56 object-cover"
                                                loading="lazy"
                                            />
                                        )}

                                        <p className="text-[13px] sm:text-sm whitespace-pre-wrap leading-[1.55]">
                                            {msg.content}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="flex justify-start">
                                    <div className="bg-white border border-[var(--line)] rounded-2xl rounded-bl-sm p-4">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* Image Preview */}
                    {imagePreview && (
                        <div className="px-3 sm:px-4 py-2 border-t border-[var(--line)] bg-white">
                            <div className="relative inline-block">
                                <img
                                    src={imagePreview}
                                    alt="preview"
                                    className="h-20 rounded-lg object-cover"
                                />
                                <button
                                    onClick={removeImage}
                                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full text-xs font-black"
                                    aria-label="이미지 제거"
                                >
                                    ✕
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="shrink-0">
                        {cookingStatus === 'finished' ? (
                            <div className="p-5 sm:p-6 border-t border-[var(--line)] bg-gradient-to-br from-[var(--g-50)] to-[var(--o-50)]">
                                <div className="text-center">
                                    <div className="text-4xl mb-3">🎉</div>
                                    <h3 className="font-black text-lg mb-2">요리 완성!</h3>
                                    <p className="text-sm text-[var(--muted)] mb-4">
                                        {recipe?.title}을(를) 성공적으로 완성했어요!
                                    </p>
                                    <button
                                        onClick={() => navigate('/')}
                                        className="w-full py-3 gradient-bg rounded-xl font-black text-sm hover:opacity-90 transition"
                                    >
                                        🏠 홈으로 돌아가기
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="p-3 sm:p-4 border-t border-[var(--line)] bg-white">
                                <div className="flex items-end gap-2">
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        accept="image/*"
                                        onChange={handleImageSelect}
                                        className="hidden"
                                    />

                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        className="w-11 h-11 grid place-items-center bg-gray-100 rounded-xl hover:bg-gray-200 transition shrink-0"
                                        title="이미지 업로드"
                                        aria-label="이미지 업로드"
                                    >
                                        📷
                                    </button>

                                    <div className="flex-1 relative">
                                        <textarea
                                            value={inputText}
                                            onChange={(e) => setInputText(e.target.value)}
                                            onCompositionStart={() => { isComposingRef.current = true; }}
                                            onCompositionEnd={() => { isComposingRef.current = false; }}
                                            onKeyDown={(e) => {
                                                const native = e.nativeEvent as any;
                                                if (isComposingRef.current || native?.isComposing) return;

                                                if (e.key === "Enter" && !e.shiftKey) {
                                                    e.preventDefault();
                                                    if (e.repeat) return; // 키 꾹 누름 방지
                                                    sendMessage();
                                                }
                                            }}
                                            placeholder={`Step ${currentStep}에서 궁금한 거 물어봐!`}
                                            rows={1}
                                            className="
                        w-full px-4 py-3
                        border border-[var(--line)]
                        rounded-xl resize-none
                        focus:outline-none focus:border-[rgba(69,197,138,.5)]
                        text-[13px] sm:text-sm
                      "
                                            style={{ minHeight: '48px', maxHeight: '120px' }}
                                        />
                                    </div>

                                    <button
                                        onClick={sendMessage}
                                        disabled={isLoading || (!inputText.trim() && !selectedImage)}
                                        className="
                      w-11 h-11
                      grid place-items-center
                      gradient-bg rounded-xl
                      font-black
                      disabled:opacity-50
                      transition hover:opacity-90
                      shrink-0
                    "
                                        aria-label="전송"
                                        title="전송"
                                    >
                                        ↑
                                    </button>
                                </div>

                                <p className="text-[11px] sm:text-xs text-[var(--muted)] mt-2 text-center font-semibold">
                                    📸 사진 찍어서 보내면 현재 Step {currentStep} 기준으로 피드백해줄게!
                                </p>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
