"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import { api, TestSession, AnswerResult, Question, MEDIA_URL } from "@/lib/api";
import { Lang, t } from "@/lib/i18n";

const EXAM_MAX_WRONG = 3;
const LETTERS = ["А", "Б", "В", "Г", "Д"];

export default function TestPage() {
  const params = useParams();
  const search = useSearchParams();
  const router = useRouter();
  const sessionKey = params.sessionKey as string;
  const lang = (search.get("lang") as Lang) ?? "ru";

  const [session, setSession] = useState<TestSession | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [explanation, setExplanation] = useState<{ ru?: string; kz?: string; media?: string; media2?: string } | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = useCallback(async () => {
    const s = await api.getSession(sessionKey);
    setSession(s);
    if (s.current_question) {
      setQuestion(s.current_question);
      setQuestionIndex(s.current_index);
    }
    setLoading(false);
    if (s.status !== "active") {
      router.replace(`/results/${sessionKey}?lang=${lang}`);
    }
  }, [sessionKey, lang, router]);

  useEffect(() => { load(); }, [load]);

  const handleAnswer = async (answerId: number) => {
    if (submitting || !session || !question) return;
    setSelectedId(answerId);
    setSubmitting(true);
    const r = await api.submitAnswer(sessionKey, question.id, answerId);
    setResult(r);
    setSession(r.session);
    if (r.explanation_media || r.explanation_ru || r.explanation2_media) {
      setExplanation({ ru: r.explanation_ru, kz: r.explanation_kz, media: r.explanation_media, media2: r.explanation2_media });
    }
    if (r.session.status !== "active") {
      setTimeout(() => router.replace(`/results/${sessionKey}?lang=${lang}`), 2000);
    }
    setSubmitting(false);
  };

  const next = () => {
    if (!session?.current_question) return;
    setQuestion(session.current_question);
    setQuestionIndex(session.current_index);
    setResult(null);
    setSelectedId(null);
    setExplanation(null);
  };

  if (loading || !session || !question) {
    return <div className="text-center py-16 text-gray-400">Загрузка...</div>;
  }

  const isAnswered = result !== null;
  const correctId = result?.correct_answer_id ?? null;
  const total = session.total;
  const answered = session.answered;

  return (
    <div className="max-w-2xl mx-auto">

      {/* ── Header ── */}
      <div className="mb-5">
        <div className="flex justify-between items-center text-sm mb-2">
          <span className="text-gray-500 font-medium">
            {t(lang, "question_label")} {questionIndex + 1}
            <span className="text-gray-300"> / </span>
            {total}
          </span>
          <div className="flex gap-3 text-sm font-medium">
            <span className="text-green-600">✅ {session.correct_count}</span>
            <span className="text-red-500">❌ {session.wrong_count}
              {session.mode === "exam" && <span className="text-gray-400 font-normal">/{EXAM_MAX_WRONG}</span>}
            </span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className="h-2.5 rounded-full transition-all duration-500"
            style={{
              width: `${(answered / total) * 100}%`,
              backgroundColor: session.wrong_count >= EXAM_MAX_WRONG - 1 && session.mode === "exam"
                ? "#ef4444" : "#3b82f6",
            }}
          />
        </div>
      </div>

      {/* ── Video ── */}
      {question.question_media && (
        <div className="mb-4 rounded-2xl overflow-hidden bg-black shadow-md">
          <video
            key={question.id}
            src={`${MEDIA_URL}/${question.question_media}`}
            controls
            autoPlay
            muted
            playsInline
            className="w-full max-h-72 object-contain"
          />
        </div>
      )}

      {/* ── Question text ── */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 px-5 py-4 mb-4">
        <p className="text-base font-medium leading-relaxed text-gray-800">
          {lang === "kz" && question.text_kz ? question.text_kz : question.text_ru}
        </p>
      </div>

      {/* ── Answers ── */}
      <div className="flex flex-col gap-2 mb-4">
        {question.answers.map((ans, idx) => {
          const text = lang === "kz" && ans.text_kz ? ans.text_kz : ans.text_ru;
          const letter = LETTERS[idx] ?? String(idx + 1);
          const isCorrect = isAnswered && ans.id === correctId;
          const isSelected = ans.id === selectedId;

          /* ─ Before answer ─ */
          if (!isAnswered) {
            return (
              <button
                key={ans.id}
                onClick={() => handleAnswer(ans.id)}
                disabled={submitting}
                className="flex items-start gap-3 text-left w-full bg-white border-2 border-gray-200
                  rounded-xl px-4 py-3.5 hover:border-blue-400 hover:bg-blue-50
                  active:scale-[0.99] transition-all cursor-pointer group"
              >
                <span className="shrink-0 w-7 h-7 rounded-full bg-gray-100 group-hover:bg-blue-100
                  flex items-center justify-center text-sm font-bold text-gray-500
                  group-hover:text-blue-600 transition-colors mt-0.5">
                  {letter}
                </span>
                <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900 leading-relaxed">
                  {text}
                </span>
              </button>
            );
          }

          /* ─ Correct answer, user selected it ─ */
          if (isCorrect && isSelected) {
            return (
              <div key={ans.id}
                className="flex items-start gap-3 bg-green-500 rounded-xl px-4 py-3.5 shadow-sm">
                <span className="shrink-0 text-xl mt-0.5">✅</span>
                <div>
                  <div className="text-xs font-bold text-green-100 uppercase tracking-wide mb-0.5">
                    {lang === "ru" ? "Ваш ответ · Правильно!" : "Сіздің жауабыңыз · Дұрыс!"}
                  </div>
                  <div className="text-sm font-medium text-white leading-relaxed">{text}</div>
                </div>
              </div>
            );
          }

          /* ─ Correct answer, user didn't pick it ─ */
          if (isCorrect && !isSelected) {
            return (
              <div key={ans.id}
                className="flex items-start gap-3 bg-green-50 border-2 border-green-500 rounded-xl px-4 py-3.5">
                <span className="shrink-0 text-xl mt-0.5">✅</span>
                <div>
                  <div className="text-xs font-bold text-green-600 uppercase tracking-wide mb-0.5">
                    {lang === "ru" ? "Правильный ответ" : "Дұрыс жауап"}
                  </div>
                  <div className="text-sm font-medium text-green-800 leading-relaxed">{text}</div>
                </div>
              </div>
            );
          }

          /* ─ Wrong answer, user selected it ─ */
          if (!isCorrect && isSelected) {
            return (
              <div key={ans.id}
                className="flex items-start gap-3 bg-red-500 rounded-xl px-4 py-3.5 shadow-sm">
                <span className="shrink-0 text-xl mt-0.5">❌</span>
                <div>
                  <div className="text-xs font-bold text-red-100 uppercase tracking-wide mb-0.5">
                    {lang === "ru" ? "Ваш ответ · Неправильно" : "Сіздің жауабыңыз · Қате"}
                  </div>
                  <div className="text-sm font-medium text-white leading-relaxed">{text}</div>
                </div>
              </div>
            );
          }

          /* ─ Other wrong answers ─ */
          return (
            <div key={ans.id}
              className="flex items-start gap-3 bg-gray-50 border-2 border-gray-100 rounded-xl px-4 py-3.5 opacity-40">
              <span className="shrink-0 w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center
                text-sm font-bold text-gray-400 mt-0.5">
                {letter}
              </span>
              <span className="text-sm font-medium text-gray-500 leading-relaxed">{text}</span>
            </div>
          );
        })}
      </div>

      {/* ── Explanation (training mode) ── */}
      {isAnswered && session.mode === "training" && explanation && (
        <div className="mb-4 rounded-2xl overflow-hidden bg-gray-900 shadow">
          <div className="px-4 py-2 bg-gray-800 text-xs font-semibold text-gray-300 uppercase tracking-wide">
            💡 {lang === "ru" ? "Объяснение" : "Түсіндірме"}
          </div>
          {(() => {
            const text = lang === "kz" && explanation.kz ? explanation.kz : explanation.ru;
            return text ? (
              <div className="px-4 py-3 text-sm text-gray-100 leading-relaxed border-t border-gray-700">
                {text}
              </div>
            ) : null;
          })()}
          {explanation.media && (
            <video
              src={`${MEDIA_URL}/${explanation.media}`}
              controls
              autoPlay
              className="w-full max-h-56 object-contain"
            />
          )}
          {explanation.media2 && (
            <video
              src={`${MEDIA_URL}/${explanation.media2}`}
              controls
              className="w-full max-h-56 object-contain border-t border-gray-700"
            />
          )}
        </div>
      )}

      {/* ── Next button ── */}
      {isAnswered && session.status === "active" && (
        <button
          onClick={next}
          className="w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white
            font-semibold py-3.5 rounded-xl transition-all shadow-sm text-base"
        >
          {t(lang, "next")} →
        </button>
      )}

      {/* ── Session failed banner ── */}
      {isAnswered && session.status === "failed" && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
          <p className="text-red-700 font-semibold">
            ❌ {lang === "ru" ? "Тест не пройден — слишком много ошибок" : "Тест тапсырылмады — тым көп қате"}
          </p>
        </div>
      )}
    </div>
  );
}
