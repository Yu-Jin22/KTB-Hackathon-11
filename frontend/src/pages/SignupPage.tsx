import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthShell from "./AuthShell";

export default function SignupPage() {
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [nickname, setNickname] = useState("");
    const [password, setPassword] = useState("");
    const [password2, setPassword2] = useState("");
    const [agree, setAgree] = useState(false);

    const [toast, setToast] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const showToast = (msg: string) => {
        setToast(msg);
        setTimeout(() => setToast(null), 2200);
    };

    const handleSignup = async () => {
        if (!username.trim() || !password.trim() || !password2.trim()) {
            showToast("필수 항목을 입력해줘!");
            return;
        }
        if (password !== password2) {
            showToast("비밀번호가 서로 달라요.");
            return;
        }
        if (!agree) {
            showToast("약관 동의가 필요해요.");
            return;
        }

        setLoading(true);
        try {
            // await signupApi({ username, password, nickname: nickname.trim() || undefined });

            showToast("회원가입 완료! 로그인해볼까요? ✅");
            setTimeout(() => navigate("/login"), 350);
        } catch (e) {
            showToast("회원가입 실패. 잠시 후 다시 시도해줘!");
        } finally {
            setLoading(false);
        }
    };

    const onKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !loading) handleSignup();
    };

    return (
        <>
            <AuthShell title="회원가입" subtitle="서비스는 공개예요. 저장/내 기록 기능만 로그인 후 사용해요.">
                <div className="flex flex-col gap-3">
                    <label className="text-xs font-black text-[rgba(23,34,51,.78)]">아이디</label>
                    <input
                        className="w-full px-4 py-3 rounded-2xl border border-[var(--line)] bg-white/[.96] outline-none font-semibold"
                        placeholder="아이디를 입력해 주세요"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        onKeyDown={onKeyDown}
                        disabled={loading}
                    />

                    <label className="text-xs font-black text-[rgba(23,34,51,.78)] mt-2">닉네임 (선택)</label>
                    <input
                        className="w-full px-4 py-3 rounded-2xl border border-[var(--line)] bg-white/[.96] outline-none font-semibold"
                        placeholder="예: 퇴근요리러"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
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

                    <label className="text-xs font-black text-[rgba(23,34,51,.78)] mt-2">비밀번호 확인</label>
                    <input
                        className="w-full px-4 py-3 rounded-2xl border border-[var(--line)] bg-white/[.96] outline-none font-semibold"
                        placeholder="••••••••"
                        value={password2}
                        onChange={(e) => setPassword2(e.target.value)}
                        type="password"
                        onKeyDown={onKeyDown}
                        disabled={loading}
                    />

                    <label className="mt-2 flex items-center gap-2 select-none cursor-pointer">
                        <input
                            type="checkbox"
                            checked={agree}
                            onChange={(e) => setAgree(e.target.checked)}
                            className="w-4 h-4"
                        />
                        <span className="text-xs font-extrabold text-[rgba(95,109,124,.98)]">
                            (필수) 서비스 이용 약관 및 개인정보 처리방침에 동의합니다.
                        </span>
                    </label>

                    <button
                        onClick={handleSignup}
                        disabled={loading}
                        className="mt-1 gradient-bg shadow-[var(--shadow2)] cursor-pointer px-4 py-[12px] rounded-2xl font-black text-[13px] transition-all text-[rgba(23,34,51,.90)] select-none hover:translate-y-[-1px] hover:brightness-[1.05] hover:shadow-[var(--shadow)] disabled:opacity-75 disabled:cursor-not-allowed"
                    >
                        {loading ? "⏳ 가입 중..." : "✨ 회원가입"}
                    </button>

                    <div className="flex items-center justify-end mt-1">
                        <button
                            className="text-xs font-extrabold text-[rgba(23,34,51,.86)]"
                            onClick={() => navigate("/login")}
                            type="button"
                        >
                            이미 계정이 있어요 → 로그인
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
