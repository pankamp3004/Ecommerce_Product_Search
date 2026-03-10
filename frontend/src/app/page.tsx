export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-slate-50 dark:bg-slate-900 transition-colors duration-300">
      <div className="z-10 w-full max-w-4xl items-center justify-between font-mono text-sm">
        <div className="flex flex-col items-center justify-center text-center mb-8">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl text-slate-900 dark:text-white mb-2">
            E-Commerce AI Assistant
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400">
            Ask for products, filter by price, or search by brands using natural language.
          </p>
        </div>
      </div>
      
      {/* The Chat Interface Component */}
      <div className="w-full max-w-4xl h-[70vh] min-h-[500px] max-h-[800px] flex shadow-2xl rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
        <Chat />
      </div>
    </main>
  );
}

import Chat from "@/components/Chat";
