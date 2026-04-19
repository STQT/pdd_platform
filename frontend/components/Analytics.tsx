"use client";
import Script from "next/script";

export default function Analytics() {
  return (
    <>
      <Script id="gtm" strategy="afterInteractive">{`
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','GTM-W2WKFVC5');
      `}</Script>
      <Script id="ym" strategy="afterInteractive">{`
        (function(m,e,t,r,i,k,a){
          m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
          m[i].l=1*new Date();
          k=e.createElement(t);k.async=1;k.src=r;
          k.onload=function(){
            m[i](108671251,'init',{webvisor:true,clickmap:true,accurateTrackBounce:true,trackLinks:true});
          };
          a=e.getElementsByTagName(t)[0];a.parentNode.insertBefore(k,a)
        })(window,document,'script','https://mc.yandex.ru/metrika/tag.js','ym');
      `}</Script>
    </>
  );
}
