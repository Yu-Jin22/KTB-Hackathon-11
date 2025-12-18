import React from "react";
import { useNavigate } from "react-router-dom";

export default function AuthShell({
    title,
    subtitle,
    children,
}: {
    title: string;
    subtitle: string;
    children: React.ReactNode;
}) {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen">
            {/* Topbar */}
            <header className="h-[72px] flex items-center justify-between px-[22px] sticky top-0 z-50 backdrop-blur-[10px] bg-white/[.78] border-b border-[var(--line)]">
                <div
                    className="flex items-center gap-3 select-none cursor-pointer"
                    onClick={() => navigate("/")}
                >
                    <div className="logo-gradient logo-shine w-10 h-10 rounded-[14px] shadow-[0_12px_22px_rgba(17,24,39,.10)] relative overflow-hidden" />
                    <h1 className="text-base m-0 tracking-[-0.3px] flex gap-2 items-baseline font-black">
                        오늘 뭐먹지
                        <span className="text-xs px-[9px] py-[3px] rounded-full border border-[var(--line)] bg-white/85 text-[rgba(23,34,51,.70)] font-extrabold">
                            beta
                        </span>
                    </h1>
                </div>

                <button
                    onClick={() => navigate("/")}
                    className="pill px-3 py-[10px] rounded-full border border-[var(--line)] bg-white/90 text-[rgba(23,34,51,.86)] text-[13px] flex gap-2 items-center cursor-pointer transition-all shadow-[var(--shadow2)] font-black hover:translate-y-[-1px] hover:bg-white/[.98] hover:shadow-[var(--shadow)]"
                >
                    ← 둘러보기
                </button>
            </header>

            <main className="w-[min(520px,calc(100%-32px))] mx-auto py-10 pb-24">
                {/* Title */}
                <section className="mt-10 text-center">
                    <h2 className="text-[40px] leading-[1.05] m-0 tracking-[-1px] font-black">
                        {title.split(" ").slice(0, 1).join(" ")}{" "}
                        <span className="gradient-text">{title.split(" ").slice(1).join(" ")}</span>
                    </h2>
                    <p className="m-0 mt-3 text-[14.5px] text-[var(--muted)] leading-[1.65] font-semibold">
                        {subtitle}
                    </p>
                </section>

                {/* Form Card Only */}
                <section className="mt-7">
                    <div className="bg-[var(--card)] border border-[var(--line)] rounded-[var(--radius)] shadow-[var(--shadow)] overflow-hidden">
                        <div className="p-[16px_18px] border-b border-[rgba(23,34,51,.08)] gradient-bg-soft">
                            <p className="m-0 text-sm font-black text-[rgba(23,34,51,.92)]">계정</p>
                            <p className="m-0 mt-1 text-xs font-semibold text-[var(--muted)]">
                                저장 기능은 로그인 후 사용할 수 있어요.
                            </p>
                        </div>
                        <div className="p-[18px]">{children}</div>
                    </div>

                    {/* Bottom Links */}
                    <div className="mt-4 flex items-center justify-center gap-2 text-xs font-extrabold text-[rgba(95,109,124,.95)]">
                        <span>분석/보기는 로그인 없이 가능</span>
                        <span className="opacity-40">·</span>
                        <button
                            type="button"
                            onClick={() => navigate("/")}
                            className="underline decoration-[rgba(95,109,124,.35)]"
                        >
                            홈으로 돌아가기
                        </button>
                    </div>
                </section>
            </main>
        </div>
    );
}
