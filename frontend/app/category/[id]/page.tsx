"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { Lang, t } from "@/lib/i18n";

export default function CategoryPage() {
  const params = useParams();
  const search = useSearchParams();
  const router = useRouter();
  const lang = (search.get("lang") as Lang) ?? "ru";
  const catId = Number(params.id);

  const start = async (mode: "training" | "exam") => {
    const session = await api.startSession(mode, catId);
    router.push(`/test/${session.session_key}?lang=${lang}`);
  };

  return (
    <div className="max-w-md mx-auto mt-12 text-center">
      <h2 className="text-xl font-bold mb-8">{t(lang, "choose_mode")}</h2>
      <div className="flex flex-col gap-4">
        <button
          onClick={() => start("training")}
          className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 rounded-xl shadow text-lg transition"
        >
          📖 {t(lang, "start_training")}
          <div className="text-sm font-normal opacity-80 mt-1">
            {lang === "ru" ? "Все вопросы, сразу видно ответ" : "Барлық сұрақтар, жауап бірден көрінеді"}
          </div>
        </button>
        <button
          onClick={() => start("exam")}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl shadow text-lg transition"
        >
          🎯 {t(lang, "start_exam")}
          <div className="text-sm font-normal opacity-80 mt-1">
            {lang === "ru" ? "20 случайных вопросов, не более 3 ошибок" : "20 кездейсоқ сұрақ, 3 қатеден аспайды"}
          </div>
        </button>
        <button
          onClick={() => router.push(`/?lang=${lang}`)}
          className="text-gray-500 hover:text-gray-700 py-2 text-sm transition"
        >
          ← {t(lang, "back_home")}
        </button>
      </div>
    </div>
  );
}
