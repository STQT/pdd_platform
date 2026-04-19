"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, SessionResults } from "@/lib/api";
import { Lang, t } from "@/lib/i18n";
import Link from "next/link";

export default function ResultsPage() {
  const params = useParams();
  const search = useSearchParams();
  const router = useRouter();
  const lang = (search.get("lang") as Lang) ?? "ru";
  const sessionKey = params.sessionKey as string;

  const [results, setResults] = useState<SessionResults | null>(null);

  useEffect(() => {
    api.getResults(sessionKey).then(setResults);
  }, [sessionKey]);

  if (!results) return <div className="text-center py-16 text-gray-400">Загрузка результатов...</div>;

  const isPassed = results.status === "passed";
  const isDone = results.status !== "active";
  const emoji = results.status === "passed" ? "✅" : results.status === "failed" ? "❌" : "🏁";

  return (
    <div className="max-w-md mx-auto text-center mt-8">
      <div className="text-6xl mb-4">{emoji}</div>
      <h2 className="text-2xl font-bold mb-1">
        {results.status === "passed"
          ? t(lang, "result_passed")
          : results.status === "failed"
          ? t(lang, "result_failed")
          : t(lang, "result_done")}
      </h2>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 my-6">
        <div className="grid grid-cols-3 gap-4 text-center mb-4">
          <div>
            <div className="text-2xl font-bold text-green-600">{results.correct_count}</div>
            <div className="text-xs text-gray-500 mt-1">
              {lang === "ru" ? "Правильно" : "Дұрыс"}
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-500">{results.wrong_count}</div>
            <div className="text-xs text-gray-500 mt-1">
              {lang === "ru" ? "Ошибок" : "Қате"}
            </div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">{results.pass_rate}%</div>
            <div className="text-xs text-gray-500 mt-1">
              {lang === "ru" ? "Результат" : "Нәтиже"}
            </div>
          </div>
        </div>

        {/* Progress visual */}
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${isPassed ? "bg-green-500" : "bg-red-400"}`}
            style={{ width: `${results.pass_rate}%` }}
          />
        </div>
        <div className="text-sm text-gray-500 mt-2">
          {results.correct_count} {t(lang, "of")} {results.total}
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <Link
          href="/"
          className="block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition"
        >
          🏠 {t(lang, "back_home")}
        </Link>
        <Link
          href={`/?lang=${lang}`}
          className="block bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 rounded-xl transition"
        >
          🔄 {t(lang, "try_again")}
        </Link>
      </div>
    </div>
  );
}
