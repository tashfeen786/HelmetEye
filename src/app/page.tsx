
"use client";

import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { ArrowRight, PlayCircle } from 'lucide-react';
import Link from 'next/link';
import { HelmetEyeLogo } from '@/components/helmet-eye-logo';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between p-4 bg-background/80 backdrop-blur-sm">
        <Link href="/" className="flex items-center gap-2">
          <HelmetEyeLogo className="w-8 h-8 text-primary" />
          <span className="text-xl font-semibold">HelmetEye</span>
        </Link>
        <Link href="/dashboard">
          <Button>
            Go to Dashboard
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </Link>
      </header>

      <main className="flex-1">
        <section className="relative flex items-center justify-center w-full h-screen">
          <Image
            src="https://placehold.co/1920x1080.png"
            alt="Bikers on a road"
            layout="fill"
            objectFit="cover"
            className="absolute inset-0 z-0 object-cover w-full h-full brightness-50"
            data-ai-hint="bikers road"
            priority
          />
          <div className="relative z-10 text-center text-white p-4 animate-fade-in-up">
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl font-headline">
              AI-Powered Helmet Detection System
            </h1>
            <p className="max-w-2xl mx-auto mt-4 text-lg md:text-xl text-primary-foreground/80">
              Ensure road safety with smart surveillance. Our AI analyzes video feeds to detect helmet usage in real-time.
            </p>
            <div className="flex flex-col justify-center gap-4 mt-8 sm:flex-row">
              <Link href="/live-feed">
                <Button size="lg" className="text-white" style={{backgroundColor: 'hsl(var(--accent))'}}>
                  <PlayCircle className="w-5 h-5 mr-2" />
                  Start Live Feed
                </Button>
              </Link>
              <Button size="lg" variant="outline" className="bg-transparent border-white text-white hover:bg-white hover:text-black">
                Learn More
              </Button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
