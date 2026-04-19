export type Lang = "ru" | "kz";

export const t = (lang: Lang, key: string): string => {
  const translations: Record<string, Record<Lang, string>> = {
    categories_title: { ru: "Категории ПДД", kz: "ЖҚЕ санаттары" },
    start_training: { ru: "Обучение", kz: "Оқу" },
    start_exam: { ru: "Экзамен (20 вопросов)", kz: "Емтихан (20 сұрақ)" },
    question_label: { ru: "Вопрос", kz: "Сұрақ" },
    of: { ru: "из", kz: "/" },
    correct: { ru: "Правильно!", kz: "Дұрыс!" },
    wrong: { ru: "Неправильно", kz: "Қате" },
    result_passed: { ru: "Сдали! ✅", kz: "Тапсырдыңыз! ✅" },
    result_failed: { ru: "Не сдали ❌", kz: "Тапсырмадыңыз ❌" },
    result_done: { ru: "Завершено 🏁", kz: "Аяқталды 🏁" },
    correct_answers: { ru: "Правильных ответов", kz: "Дұрыс жауаптар" },
    try_again: { ru: "Пройти ещё раз", kz: "Қайта өту" },
    back_home: { ru: "На главную", kz: "Басты бетке" },
    next: { ru: "Далее", kz: "Келесі" },
    explanation: { ru: "Объяснение", kz: "Түсіндірме" },
    all_categories: { ru: "Все категории", kz: "Барлық санаттар" },
    questions: { ru: "вопросов", kz: "сұрақ" },
    exam_mode: { ru: "Режим экзамена", kz: "Емтихан режимі" },
    training_mode: { ru: "Режим обучения", kz: "Оқу режимі" },
    choose_mode: { ru: "Выберите режим:", kz: "Режимді таңдаңыз:" },
    errors_left: { ru: "ошибок осталось", kz: "қате қалды" },
  };
  return translations[key]?.[lang] ?? key;
};

export function getText(obj: { text_ru?: string; text_kz?: string } | undefined, lang: Lang): string {
  if (!obj) return "";
  return (lang === "kz" && obj.text_kz) ? obj.text_kz : obj.text_ru ?? "";
}
