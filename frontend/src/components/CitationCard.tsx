'use client';

import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface CitationProps {
    act: string;
    section: string;
    summary: string;
    url?: string;
}

export function CitationCard({ act, section, summary, url }: CitationProps) {
    const ref = useRef<HTMLDivElement>(null);

    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const mouseXSpring = useSpring(x);
    const mouseYSpring = useSpring(y);

    const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["17.5deg", "-17.5deg"]);
    const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-17.5deg", "17.5deg"]);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
        if (!ref.current) return;

        const rect = ref.current.getBoundingClientRect();

        const width = rect.width;
        const height = rect.height;

        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const xPct = mouseX / width - 0.5;
        const yPct = mouseY / height - 0.5;

        x.set(xPct);
        y.set(yPct);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
    };

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            style={{
                rotateX,
                rotateY,
                transformStyle: "preserve-3d",
            }}
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="glass-card rounded-xl p-6 mb-4 cursor-pointer relative overflow-hidden group"
        >
            <div
                style={{ transform: "translateZ(50px)" }}
                className="relative z-10"
            >
                <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-white text-lg tracking-wide drop-shadow-md">
                        {act}
                    </h3>
                    <span className="bg-white/20 backdrop-blur-md text-white border border-white/30 text-xs px-3 py-1 rounded-full font-medium shadow-sm">
                        Section {section}
                    </span>
                </div>
                <p className="text-gray-100 text-sm leading-relaxed drop-shadow-sm font-light">
                    {summary}
                </p>

                {url && (
                    <div className="mt-3 flex justify-end">
                        <span className="text-xs text-indigo-200 hover:text-white flex items-center gap-1 transition-colors">
                            Read Full Text on Indian Kanoon ↗
                        </span>
                    </div>
                )}
            </div>

            {/* Animated Glow Gradient */}
            <div
                className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{ transform: "translateZ(20px)" }}
            />
        </motion.div>
    );
}
