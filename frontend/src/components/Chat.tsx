"use client";

import { useState, useRef, useEffect } from "react";
import { Send, User, Bot, Loader2, ListFilter } from "lucide-react";
import axios from "axios";

// Types corresponding to our FastAPI models
type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your AI personal shopping assistant. I can help you find products, filter by prices or brands, and give recommendations. Try asking: 'I am looking for campus shoes for my brother's wedding under 5000'.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom of the chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Add user message to UI
    const userMessage: Message = { role: "user", content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      // Send the entire chat history to the FastAPI backend
      const response = await axios.post("http://127.0.0.1:8001/chat", {
        messages: newMessages,
      });

      if (response.data && response.data.role && response.data.content) {
        setMessages((prev) => [...prev, response.data]);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I am having trouble connecting to the server. Please check if the FastAPI backend is running.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full h-full">
      {/* Header */}
      <div className="flex items-center px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-sm">
        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center mr-4">
          <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-200">Personal Shopper</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Online
          </p>
        </div>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50 dark:bg-slate-900/20">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex w-full ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`flex max-w-[80%] ${m.role === "user" ? "flex-row-reverse" : "flex-row"} items-start gap-4`}>
              {/* Avatar */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 
                ${m.role === "user" 
                  ? "bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300" 
                  : "bg-blue-600 text-white shadow-md shadow-blue-500/20"}`}>
                {m.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
              </div>
              
              {/* Message Bubble */}
              <div
                className={`flex text-sm sm:text-base px-5 py-3.5 rounded-2xl shadow-sm whitespace-pre-wrap
                  ${m.role === "user"
                    ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900 rounded-tr-none"
                    : "bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-700 rounded-tl-none font-medium leading-relaxed"
                  }`}
              >
                {m.content}
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex w-full justify-start">
            <div className="flex flex-row items-center gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 text-white shadow-md shadow-blue-500/20 flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm flex items-center gap-2">
                 <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                 <span className="text-sm text-slate-500 dark:text-slate-400">Browsing catalog...</span>
              </div>
            </div>
          </div>
        )}
        
        {/* Invisible div to target for auto-scrolling */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-white/50 dark:bg-slate-950/50 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="relative flex items-center w-full">
          <div className="absolute left-4 text-slate-400 pointer-events-none">
             <ListFilter className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Type your message... e.g., 'campus shoes under 5000'"
            className="w-full py-4 pl-12 pr-16 bg-slate-100 dark:bg-slate-900 border-none rounded-xl focus:ring-2 focus:ring-blue-500/50 outline-none text-slate-800 dark:text-slate-200 transition-all placeholder:text-slate-400"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:hover:bg-blue-600 flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        <div className="text-center mt-3">
          <p className="text-[10px] text-slate-400 font-medium tracking-wide">AI RECCOMENDATIONS POWERED BY OPENAI</p>
        </div>
      </div>
    </div>
  );
}
