"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { api, TestSession, AnswerResult, MEDIA_URL } from "@/lib/api";
import { Lang, t, getText } from "@/lib/i18n";

const EXAM_MAX_WRONG = 3;

export default function TestPage() {
  const params = useParams();
  const search = useSearchParams();
  const router = useRouter();
  const sessionKey = params.sessionKey as string;
  const lang = (search.get("lang") as Lang) ?? "ru";

  const [session, setSession] = useState<TestSession | null>(null);
  const [lastResult, setLastResult] = useState<AnswerResult | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    const s = await api.getSession(sessionKey);
    setSession(s);
    setLoading(false);
    if (s.status !== "active") {
      router.replace(`/results/${sessionKey}?lang=${lang}`);
    }
  }, [sessionKey, lang, router]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAnswer = async (answerId: number) => {
    if (submitting || !session?.current_question) return;
    setSelectedId(answerId);
    setSubmitting(true);

    const result = await api.submitAnswer(sessionKey, session.current_question.id, answerId);
    setLastResult(result);
    setSession(result.session);

    if (result.session.status !== "active") {
      setTimeout(() => router.replace(`/results/${sessionKey}?lang=${lang}`), 1500);
    }
    setSubmitting(false);
  };

  const next = () => {
    setLastResult(null);
    setSelectedId(null);
  };

  if (loading || !session) {
    return <div className="text-center py-16 text-gray-400">Загрузка...</div>;
  }

  const q = session.current_question;
  if (!q) return null;

  const isTraining = session.mode === "training";
  const isAnswered = lastResult !== null;
  const errorsLeft = isTraining ? null : EXAM_MAX_WRONG - session.wrong_count;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-500 mb-1">
          <span>
            {t(lang, "question_label")} {session.current_index + 1} {t(lang, "of")} {session.total}
          </span>
          {errorsLeft !== null && (
            <span className={`font-medium ${errorsLeft <= 1 ? "text-red-500" : "text-gray-600"}`}>
              ❌ {session.wrong_count}/{EXAM_MAX_WRONG}
            </span>
          )}
          <span className="text-green-600">✅ {session.correct_count}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${(session.answered / session.total) * 100}%` }}
          />
        </div>
      </div>

      {/* Media */}
      {q.question_media && (
        <div className="mb-4 rounded-xl overflow-hidden bg-black">
          <video
            src={`${MEDIA_URL}/${q.question_media}`}
            controls
            autoPlay
            muted
            className="w-full max-h-64 object-contain"
          />
        </div>
      )}

      {/* Question text */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 mb-4">
        <p className="text-base font-medium leading-relaxed">
          {lang === "kz" && q.text_kz ? q.text_kz : q.text_ru}
        </p>
      </div>

      {/* Answers */}
      <div className="flex flex-col gap-2 mb-4">
        {q.answers.map((ans) => {
          let style =
            "text-left bg-white border-2 border-gray-200 rounded-xl px-4 py-3 text-sm font-medium transition ";

          if (isAnswered) {
            if (ans.is_correct) {
              style += "border-green-500 bg-green-50 text-green-800";
            } else if (ans.id === selectedId && !ans.is_correct) {
              style += "border-red-400 bg-red-50 text-red-700";
            } else {
              style += "opacity-50";
            }
          } else {
            style += "hover:border-blue-400 hover:bg-blue-50 cursor-pointer";
          }

          return (
            <button
              key={ans.id}
              className={style}
              onClick={() => !isAnswered && handleAnswer(ans.id)}
              disabled={isAnswered || submitting}
            >
              {lang === "kz" && ans.text_kz ? ans.text_kz : ans.text_ru}
            </button>
          );
        })}
      </div>

      {/* Feedback (training mode) */}
      {isAnswered && isTraining && (
        <div className={`rounded-xl p-4 mb-4 ${lastResult?.is_correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
          <p className={`font-semibold ${lastResult?.is_correct ? "text-green-700" : "text-red-700"}`}>
            {lastResult?.is_correct ? t(lang, "correct") : t(lang, "wrong")}
          </p>
          {lastResult?.explanation_media && (
            <video
              src={`${MEDIA_URL}/${lastResult.explanation_media}`}
              controls
              className="mt-3 w-full rounded-lg max-h-48"
            />
          )}
        </div>
      )}

      {/* Next button */}
      {isAnswered && (
        <button
          onClick={next}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition"
        >
          {t(lang, "next")} →
        </button>
      )}
    </div>
  );
}
