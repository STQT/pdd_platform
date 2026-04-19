const API_URL = process.env.NEXT_PUBLIC_API_URL!;
export const MEDIA_URL = process.env.NEXT_PUBLIC_MEDIA_URL!;

export type Lang = "ru" | "kz";

export interface Category {
  id: number;
  title_ru: string;
  title_kz: string;
  order: number;
  question_count: number;
}

export interface Answer {
  id: number;
  original_id: number;
  text_ru: string;
  text_kz: string;
  order: number;
  is_correct: boolean;
}

export interface Question {
  id: number;
  original_id: number;
  category_id: number;
  text_ru: string;
  text_kz: string;
  question_media: string;
  explanation_ru: string;
  explanation_kz: string;
  explanation_media: string;
  explanation2_media: string;
  correct_answer_index: number;
  answers: Answer[];
}

export interface TestSession {
  session_key: string;
  category_id: number | null;
  mode: "training" | "exam";
  status: "active" | "passed" | "failed";
  current_index: number;
  correct_count: number;
  wrong_count: number;
  total: number;
  answered: number;
  current_question: Question | null;
  created_at: string;
  finished_at: string | null;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_answer_id: number;
  explanation_ru?: string;
  explanation_kz?: string;
  explanation_media?: string;
  explanation2_media?: string;
  session: TestSession;
}

export interface SessionResults {
  session_key: string;
  mode: "training" | "exam";
  status: string;
  correct_count: number;
  wrong_count: number;
  total: number;
  pass_rate: number;
  answers: { question_id: number; answer_id: number; is_correct: boolean }[];
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  categories: (): Promise<Category[]> => req("/categories/"),

  startSession: (
    mode: "training" | "exam",
    category_id?: number
  ): Promise<TestSession> =>
    req("/sessions/", {
      method: "POST",
      body: JSON.stringify({ mode, category_id: category_id ?? null }),
    }),

  getSession: (key: string): Promise<TestSession> => req(`/sessions/${key}/`),

  submitAnswer: (
    key: string,
    question_id: number,
    answer_id: number
  ): Promise<AnswerResult> =>
    req(`/sessions/${key}/answer/`, {
      method: "POST",
      body: JSON.stringify({ question_id, answer_id }),
    }),

  getResults: (key: string): Promise<SessionResults> =>
    req(`/sessions/${key}/results/`),
};
