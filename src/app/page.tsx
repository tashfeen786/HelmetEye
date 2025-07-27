
"use client";

import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { ArrowRight, PlayCircle, Video, Upload, FileText, Cpu } from 'lucide-react';
import Link from 'next/link';
import { HelmetEyeLogo } from '@/components/helmet-eye-logo';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useRef } from 'react';

export default function LandingPage() {
  const aboutRef = useRef<HTMLDivElement>(null);

  const handleLearnMoreClick = () => {
    aboutRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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
              <Button size="lg" variant="outline" className="bg-transparent border-white text-white hover:bg-white hover:text-black" onClick={handleLearnMoreClick}>
                Learn More
              </Button>
            </div>
          </div>
        </section>

        <section ref={aboutRef} className="py-20 bg-muted/40">
            <div className="container mx-auto px-4">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold tracking-tight font-headline">How HelmetEye Works</h2>
                    <p className="text-muted-foreground mt-2 max-w-2xl mx-auto">
                        Our platform leverages cutting-edge AI to provide a comprehensive solution for monitoring road safety and ensuring helmet compliance.
                    </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <Card className="text-center">
                        <CardHeader>
                            <div className="mx-auto bg-primary/10 text-primary p-3 rounded-full w-fit">
                                <Video className="w-8 h-8"/>
                            </div>
                           <CardTitle>Real-Time Detection</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">Analyze live video streams from traffic cameras to detect helmet usage instantly and provide real-time alerts.</p>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardHeader>
                            <div className="mx-auto bg-primary/10 text-primary p-3 rounded-full w-fit">
                                <Upload className="w-8 h-8"/>
                            </div>
                            <CardTitle>Image & Video Upload</CardTitle>
                        </CardHeader>
                        <CardContent>
                             <p className="text-muted-foreground">Upload pre-recorded videos or images to run detections and analyze past incidents with the same powerful AI.</p>
                        </CardContent>
                    </Card>
                    <Card className="text-center">
                        <CardHeader>
                            <div className="mx-auto bg-primary/10 text-primary p-3 rounded-full w-fit">
                               <FileText className="w-8 h-8"/>
                            </div>
                           <CardTitle>Detailed Reporting</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">Generate comprehensive reports with detection statistics, visual evidence, and filtering capabilities to track compliance over time.</p>
                        </CardContent>
                    </Card>
                     <Card className="text-center">
                        <CardHeader>
                            <div className="mx-auto bg-primary/10 text-primary p-3 rounded-full w-fit">
                                <Cpu className="w-8 h-8"/>
                            </div>
                            <CardTitle>AI-Powered Analysis</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground">Our system is built on a sophisticated AI model trained to accurately identify bikers and helmets in various conditions.</p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </section>
      </main>
    </div>
  );
}
