'use client';

import React, { useState, useEffect, useRef } from 'react';
import { VoiceInput } from '@/components/VoiceInput';
import { CitationCard } from '@/components/CitationCard';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Scale, Info, ShieldCheck } from 'lucide-react';

interface Citation {
  act: string;
  section: string;
  summary: string;
}

interface QueryResponse {
  domain: string;
  relevant_laws: string[];
  explanation: string;
  general_guidance: string;
  confidence: string;
  disclaimer: string;
  citations: Citation[];
}

interface Message {
  type: 'user' | 'bot';
  content: string | QueryResponse;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const speakText = (text: string, lang: string = 'dist') => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleQuery = async (text: string) => {
    if (!text.trim()) return;

    setMessages(prev => [...prev, { type: 'user', content: text }]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, language: 'hi' }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data: QueryResponse = await response.json();
      setMessages(prev => [...prev, { type: 'bot', content: data }]);

      const speechText = `${data.explanation} ${data.general_guidance}`;
      speakText(speechText);

    } catch (error) {
      console.error('Error fetching query:', error);
      setMessages(prev => [...prev, { type: 'bot', content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-transparent relative overflow-hidden">

      {/* 3D Glass Header */}
      <header className="fixed top-0 left-0 right-0 z-50 p-4">
        <div className="container mx-auto">
          <div className="glass-panel mx-auto max-w-5xl rounded-full px-6 py-3 flex justify-between items-center shadow-lg backdrop-blur-xl bg-white/10 border border-white/20">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full shadow-inner">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-white drop-shadow-sm">Samvidhan.ai</h1>
            </div>
            <span className="text-xs font-medium text-indigo-100 bg-white/10 px-3 py-1 rounded-full border border-white/10">
              Bilingual Legal AI
            </span>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 container mx-auto p-4 flex flex-col gap-6 overflow-y-auto pb-32 pt-28 max-w-5xl">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center text-white/80 mt-12 flex flex-col items-center justify-center h-full"
          >
            <div className="w-24 h-24 bg-gradient-to-tr from-indigo-500 to-rose-500 rounded-3xl rotate-12 flex items-center justify-center shadow-2xl mb-8 backdrop-blur-sm border border-white/20">
              <Scale className="w-12 h-12 text-white" />
            </div>
            <h2 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">Welcome to Samvidhan.ai</h2>
            <p className="max-w-md mx-auto text-lg text-indigo-100/80 leading-relaxed">
              Ask me anything about Indian Law in Hindi or English.
              I provide accurate guidance based on statutory sources.
            </p>
          </motion.div>
        )}

        <AnimatePresence mode="popLayout">
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 20 }}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%] md:max-w-2xl rounded-3xl p-6 shadow-xl backdrop-blur-md border ${msg.type === 'user'
                ? 'bg-gradient-to-br from-indigo-600/90 to-blue-600/90 text-white rounded-br-none border-indigo-400/30'
                : 'glass-panel text-white rounded-bl-none border-white/10'
                }`}>
                {msg.type === 'user' ? (
                  <p className="text-lg font-medium">{msg.content as string}</p>
                ) : (
                  <div className="space-y-5">
                    {typeof msg.content === 'string' ? (
                      <p>{msg.content}</p>
                    ) : (
                      <>
                        {/* Confidence Badge */}
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider shadow-sm border ${(msg.content as QueryResponse).confidence === 'High' ? 'bg-green-500/20 text-green-200 border-green-500/30' :
                              (msg.content as QueryResponse).confidence === 'Medium' ? 'bg-yellow-500/20 text-yellow-200 border-yellow-500/30' :
                                'bg-red-500/20 text-red-200 border-red-500/30'
                            }`}>
                            {(msg.content as QueryResponse).confidence} Confidence
                          </span>
                          <span className="text-xs text-indigo-200 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            {(msg.content as QueryResponse).domain}
                          </span>
                        </div>

                        {/* Explanation */}
                        <div className="prose prose-invert prose-p:text-white/90 prose-headings:text-white max-w-none">
                          <p className="text-lg leading-relaxed">{(msg.content as QueryResponse).explanation}</p>
                        </div>

                        {/* Guidance */}
                        <div className="bg-white/5 p-4 rounded-xl text-sm text-indigo-100 border border-white/10 flex gap-3">
                          <Info className="w-5 h-5 text-indigo-400 shrink-0" />
                          <p><strong>Guidance:</strong> {(msg.content as QueryResponse).general_guidance}</p>
                        </div>

                        {/* Citations */}
                        {(msg.content as QueryResponse).citations.length > 0 && (
                          <div className="mt-6">
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                              Source Materials
                              <span className="h-px flex-1 bg-white/10"></span>
                            </h4>
                            <div className="space-y-3">
                              {(msg.content as QueryResponse).citations.map((cite, cIdx) => (
                                <CitationCard key={cIdx} {...cite} />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Disclaimer */}
                        <div className="text-[11px] text-white/40 border-t border-white/10 pt-3 mt-2 flex items-center gap-2">
                          <ShieldCheck className="w-3 h-3" />
                          {(msg.content as QueryResponse).disclaimer}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="glass-panel p-4 rounded-3xl rounded-bl-none flex items-center gap-3">
              <div className="w-2.5 h-2.5 bg-indigo-400 rounded-full animate-[bounce_1s_infinite_0ms]"></div>
              <div className="w-2.5 h-2.5 bg-purple-400 rounded-full animate-[bounce_1s_infinite_200ms]"></div>
              <div className="w-2.5 h-2.5 bg-rose-400 rounded-full animate-[bounce_1s_infinite_400ms]"></div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 fixed bottom-0 left-0 right-0 z-40 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent pb-8">
        <div className="container mx-auto max-w-4xl flex items-center gap-4">
          <VoiceInput onTranscript={handleQuery} />
          <form
            className="flex-1 relative group"
            onSubmit={(e) => {
              e.preventDefault();
              const input = e.currentTarget.elements.namedItem('query') as HTMLInputElement;
              handleQuery(input.value);
              input.value = '';
            }}
          >
            <input
              type="text"
              name="query"
              placeholder="Ask Samvidhan.ai (or try voice)..."
              className="w-full bg-white/10 text-white placeholder-white/40 rounded-full px-8 py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:bg-white/15 transition-all shadow-lg border border-white/10 backdrop-blur-md"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="absolute right-2 top-2 bottom-2 bg-indigo-600 text-white rounded-full p-2.5 hover:bg-indigo-500 transition-all custom-shadow disabled:opacity-50 disabled:hover:bg-indigo-600"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
