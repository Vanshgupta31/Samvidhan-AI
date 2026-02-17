'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface VoiceInputProps {
  onTranscript: (text: string) => void;
}

export function VoiceInput({ onTranscript }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      // @ts-ignore
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'hi-IN'; // Default to Hindi-English mix

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        onTranscript(transcript);
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        // You might want to notify the parent component or show a toast here
      };

      setRecognition(recognition);
    }
  }, [onTranscript]);

  const toggleListening = () => {
    if (isListening) {
      recognition?.stop();
    } else {
      recognition?.start();
    }
  };

  if (!recognition) {
    return null; // Speech API not supported
  }

  return (
    <div className="relative flex items-center justify-center">
      {/* Pulsating 3D Glow Ring */}
      {isListening && (
        <motion.div
          initial={{ scale: 1, opacity: 0.5 }}
          animate={{ scale: 1.5, opacity: 0 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
          className="absolute inset-0 rounded-full bg-red-500 blur-md z-0"
        />
      )}

      {/* Main Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={toggleListening}
        className={`relative z-10 p-4 rounded-full transition-all duration-300 ${isListening
            ? 'bg-gradient-to-r from-red-600 to-rose-500 shadow-[0_0_20px_rgba(220,38,38,0.6)] border border-red-400'
            : 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:shadow-[0_0_20px_rgba(79,70,229,0.5)] border border-indigo-400'
          } text-white shadow-lg backdrop-blur-sm`}
        title={isListening ? 'Stop Listening' : 'Start Voice Input'}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
          className="w-6 h-6 drop-shadow-md"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 1.5a3 3 0 013 3v1.5a3 3 0 01-6 0v-1.5a3 3 0 013-3z"
          />
        </svg>
      </motion.button>
    </div>
  );
}
