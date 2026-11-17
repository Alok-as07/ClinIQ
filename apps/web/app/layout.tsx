import "./globals.css";
import Nav from "@/components/Nav";

export const metadata = { title: "Clinical Intelligence" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="bg-[#f5f8fa]">
      <body className="app-shell text-slate-900">
        <Nav />
        <main className="mx-auto max-w-6xl px-5 py-8 sm:px-8 lg:py-10">{children}</main>
      </body>
    </html>
  );
}