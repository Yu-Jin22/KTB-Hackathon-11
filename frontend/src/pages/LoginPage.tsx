import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AuthShell from "./AuthShell";
import { loginApi } from "../api";

export default function LoginPage() {
    const navigate = useNavigate();
    const location = useLocation() as any;

    const [email, setEmail] = useState(""); // email이면 email로 바꿔
    const [password, setPassword] = useState("");
    const [toast, setToast] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const showToast = (msg: string) => {
        setToast(msg);
        setTimeout(() => setToast(null), 2200);
    };

    const handleLogin = async () => {
        if (!email.trim() || !password.trim()) {
            showToast("아이디/비밀번호를 입력해줘!");
            return;
        }

        setLoading(true);
        try {
            await loginApi({ email, password });

            showToast("로그인 완료! 저장 기능을 사용할 수 있어요 ✅");
            const from = location?.state?.from || "/";
            setTimeout(() => navigate(from), 250);
        } catch (e: any) {
            showToast("로그인 실패. 정보를 확인해줘!");
        } finally {
            setLoading(false);
        }
    };

    const onKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !loading) handleLogin();
    };

    return (
        <>
            <AuthShell title="로그인" subtitle="레시피 추출은 누구나 가능! 마음에 드는 레시피는 내 계정에 저장해요.">
                <div className="flex flex-col gap-3">
                    {location?.state?.reason === "save" && (
                        <div className="p-3 rounded-2xl border border-[var(--line)] bg-[var(--o-50)] text-[13px] font-extrabold text-[rgba(23,34,51,.85)]">
                            ⭐ 레시피 저장은 로그인 후 사용할 수 있어요.
                        </div>
                    )}

                    <label className="text-xs font-black text-[rgba(23,34,51,.78)]">아이디</label>
                    <input
                        className="w-full px-4 py-3 rounded-2xl border border-[var(--line)] bg-white/[.96] outline-none font-semibold"
                        placeholder="아이디를 입력해 주세요"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        onKeyDown={onKeyDown}
                        disabled={loading}
                    />

                    <label className="text-xs font-black text-[rgba(23,34,51,.78)] mt-2">비밀번호</label>
                    <input
                        className="w-full px-4 py-3 rounded-2xl border border-[var(--line)] bg-white/[.96] outline-none font-semibold"
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        type="password"
                        onKeyDown={onKeyDown}
                        disabled={loading}
                    />

                    <button
                        onClick={handleLogin}
                        disabled={loading}
                        className="mt-2 gradient-bg shadow-[var(--shadow2)] cursor-pointer px-4 py-[12px] rounded-2xl font-black text-[13px] transition-all text-[rgba(23,34,51,.90)] select-none hover:translate-y-[-1px] hover:brightness-[1.05] hover:shadow-[var(--shadow)] disabled:opacity-75 disabled:cursor-not-allowed"
                    >
                        {loading ? "⏳ 로그인 중..." : "✨ 로그인"}
                    </button>

                    <div className="flex items-center justify-between mt-1">
                        <button
                            className="text-xs font-extrabold text-[rgba(95,109,124,.98)] underline decoration-[rgba(95,109,124,.35)]"
                            onClick={() => showToast("비밀번호 찾기는 다음 버전에!")}
                            type="button"
                        >
                            비밀번호를 잊었어요
                        </button>
                        <button
                            className="text-xs font-extrabold text-[rgba(23,34,51,.86)]"
                            onClick={() => navigate("/signup")}
                            type="button"
                        >
                            회원가입 →
                        </button>
                    </div>
                </div>
            </AuthShell>

            {toast && (
                <div className="fixed left-1/2 bottom-[26px] -translate-x-1/2 bg-[rgba(23,34,51,.90)] text-white/[.95] px-3 py-[10px] rounded-[14px] shadow-[0_18px_40px_rgba(17,24,39,.16)] text-[13px] max-w-[min(560px,calc(100%-24px))] text-center font-extrabold toast-animate">
                    {toast}
                </div>
            )}
        </>
    );
}
