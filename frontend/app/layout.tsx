import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "PDD Test — Тесты ПДД Казахстана",
  description: "Подготовка к экзамену ПДД Казахстана. Казахстан ЖҚЕ сынақтары.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        {/* Google Tag Manager */}
        <Script id="gtm" strategy="afterInteractive">{`
          (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
          new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
          j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
          'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
          })(window,document,'script','dataLayer','GTM-W2WKFVC5');
        `}</Script>
        {/* Yandex Metrika */}
        <Script id="ym" strategy="afterInteractive">{`
          var s = document.createElement('script');
          s.async = true;
          s.src = 'https://mc.yandex.ru/metrika/tag.js?id=108671251';
          s.onload = function() {
            window.ym(108671251,'init',{webvisor:true,clickmap:true,ecommerce:"dataLayer",accurateTrackBounce:true,trackLinks:true});
          };
          document.head.appendChild(s);
        `}</Script>
      </head>
      <body className="min-h-screen bg-gray-50">
        {/* GTM noscript */}
        <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W2WKFVC5" height="0" width="0" style={{display:"none",visibility:"hidden"}}></iframe></noscript>
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
