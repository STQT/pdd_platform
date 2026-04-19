import type { Metadata } from "next";
import Analytics from "@/components/Analytics";
import "./globals.css";

export const metadata: Metadata = {
  title: "PDD Test — Тесты ПДД Казахстана",
  description: "Подготовка к экзамену ПДД Казахстана. Казахстан ЖҚЕ сынақтары.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-gray-50">
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W2WKFVC5" height="0" width="0" style={{display:"none",visibility:"hidden"}}></iframe></noscript>
        <Analytics />
        <header className="bg-blue-600 text-white shadow-md">
          <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="text-xl font-bold tracking-tight">
              🚗 PDD Test KZ
            </a>
            <span className="text-sm opacity-80">pddtest.leetcode.uz</span>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-4 py-8">{children}</main>
        <footer className="text-center text-gray-400 text-sm py-6 mt-auto">
          PDD Test KZ — Для подготовки к экзамену ПДД
        </footer>
      </body>
    </html>
  );
}
