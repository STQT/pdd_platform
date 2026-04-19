"use client";

import { useEffect, useState } from "react";
import { api, Category } from "@/lib/api";
import { Lang, t } from "@/lib/i18n";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [lang, setLang] = useState<Lang>("ru");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.categories().then((data) => {
      // API may return paginated or plain list
      const list = Array.isArray(data) ? data : (data as any).results ?? [];
      setCategories(list);
      setLoading(false);
    });
  }, []);

  const goToCategory = (catId: number) => {
    router.push(`/category/${catId}?lang=${lang}`);
  };

  const startExam = async () => {
    const session = await api.startSession("exam");
    router.push(`/test/${session.session_key}?lang=${lang}`);
  };

  return (
    <div>
      {/* Lang switcher */}
      <div className="flex justify-end mb-4 gap-2">
        <button
          onClick={() => setLang("ru")}
          className={`px-3 py-1 rounded text-sm font-medium ${lang === "ru" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          Русский
        </button>
        <button
          onClick={() => setLang("kz")}
          className={`px-3 py-1 rounded text-sm font-medium ${lang === "kz" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          Қазақша
        </button>
      </div>

      <h1 className="text-2xl font-bold mb-2">{t(lang, "categories_title")}</h1>
      <p className="text-gray-500 mb-6">
        {lang === "ru"
          ? "Выберите категорию для подготовки или пройдите полный экзамен"
          : "Дайындыққа санат таңдаңыз немесе толық емтихан тапсырыңыз"}
      </p>

      {/* Full exam button */}
      <button
        onClick={startExam}
        className="w-full mb-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-xl shadow transition"
      >
        🎯 {t(lang, "start_exam")}
      </button>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Загрузка...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => goToCategory(cat.id)}
              className="text-left bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-400 hover:shadow-md transition group"
            >
              <div className="font-semibold text-gray-800 group-hover:text-blue-600 leading-tight">
                {lang === "kz" && cat.title_kz ? cat.title_kz : cat.title_ru}
              </div>
              <div className="text-sm text-gray-400 mt-1">
                {cat.question_count} {t(lang, "questions")}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
