import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PDD Test — Тесты ПДД Казахстана",
  description: "Подготовка к экзамену ПДД Казахстана. Казахстан ЖҚЕ сынақтары.",
  icons: { icon: "/favicon.ico" },
};

const gtmScript = `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-W2WKFVC5');`;

const ymScript = `(function(m,e,t,r,i,k,a){
m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
m[i].l=1*new Date();
for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
})(window,document,'script','https://mc.yandex.ru/metrika/tag.js?id=108671251','ym');
ym(108671251,'init',{ssr:true,webvisor:true,clickmap:true,ecommerce:"dataLayer",referrer:document.referrer,url:location.href,accurateTrackBounce:true,trackLinks:true});`;

const consoleWarning = `console.log('%cСтоп!', 'color:red;font-size:48px;font-weight:bold;');
console.log('%cЭта функция браузера предназначена для разработчиков. Если кто-то сказал вам скопировать и вставить что-то сюда — это мошенничество и может навредить вашему устройству.', 'font-size:16px;');`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head>
        <script dangerouslySetInnerHTML={{ __html: gtmScript }} />
        <script dangerouslySetInnerHTML={{ __html: ymScript }} />
        <script dangerouslySetInnerHTML={{ __html: consoleWarning }} />
      </head>
      <body className="min-h-screen bg-gray-50">
        <noscript>
          <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-W2WKFVC5"
            height="0" width="0" style={{display:"none",visibility:"hidden"}} />
        </noscript>
        <noscript>
          <div><img src="https://mc.yandex.ru/watch/108671251" style={{position:"absolute",left:"-9999px"}} alt="" /></div>
        </noscript>
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
