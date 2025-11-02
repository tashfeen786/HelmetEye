"use client";

import { useState, useEffect } from "react";
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { LayoutGrid, History, Video, CameraOff, VideoOff, Play, Loader2 } from "lucide-react";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";

export default function LiveFeedPage() {
  const [isLive, setIsLive] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isStartingStream, setIsStartingStream] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleToggleStream = async () => {
    setIsStartingStream(true);
    try {
      if (!isLive) {
        // ✅ Start stream: the <img> tag will handle MJPEG
        setIsLive(true);
        toast({
          title: "Live feed started",
          description: "Streaming from server has begun.",
        });
      } else {
        // ✅ Stop backend stream
        await fetch("http://localhost:8000/api/stop_stream");
        setIsLive(false);
        toast({
          title: "Live feed stopped",
          description: "Streaming from server has ended.",
        });
      }
    } catch (err) {
      console.error(err);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Could not toggle live feed.",
      });
    } finally {
      setIsStartingStream(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-svh bg-muted/40">
        <div className="hidden md:flex flex-col w-64 border-r bg-background">
          <div className="p-4 border-b">
            <Skeleton className="h-8 w-32" />
          </div>
          <div className="flex flex-col p-4 space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
        <div className="flex-1 p-8">
          <Skeleton className="h-10 w-48 mb-6" />
          <Card>
            <CardHeader>
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-4 w-96 mt-2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="w-full aspect-video" />
              <div className="mt-4 flex gap-4">
                <Skeleton className="w-full h-10" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <Link href="/" className="flex items-center gap-2 p-2" role="button">
            <HelmetEyeLogo className="w-8 h-8 text-primary" />
            <span className="text-lg font-semibold group-data-[collapsible=icon]:hidden">
              HelmetEye
            </span>
          </Link>
        </SidebarHeader>
        <SidebarContent>
          <SidebarMenu>
            <SidebarMenuItem>
              <Link href="/dashboard" className="w-full">
                <SidebarMenuButton>
                  <LayoutGrid />
                  <span className="group-data-[collapsible=icon]:hidden">Dashboard</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link href="/live-feed" className="w-full">
                <SidebarMenuButton isActive>
                  <Video />
                  <span className="group-data-[collapsible=icon]:hidden">Live Feed</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link href="/reports" className="w-full">
                <SidebarMenuButton>
                  <History />
                  <span className="group-data-[collapsible=icon]:hidden">Reports</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarContent>
      </Sidebar>
      <SidebarInset>
        <div className="flex flex-col min-h-svh">
          <header className="sticky top-0 z-10 flex items-center h-16 px-4 bg-background/80 backdrop-blur-sm border-b gap-4">
            <SidebarTrigger className="md:hidden" />
            <h1 className="text-xl font-semibold">Live Feed</h1>
          </header>
          <main className="flex-1 p-4 md:p-6 lg:p-8">
            <Card>
              <CardHeader>
                <CardTitle>Live Detection Feed</CardTitle>
                <CardDescription>Stream served by backend with helmet detection.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="relative aspect-video w-full bg-muted rounded-lg overflow-hidden">
                  {isLive ? (
                    <img
                      src="http://localhost:8000/api/start_stream"
                      alt="Live Detection Feed"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 text-white p-4">
                      <CameraOff className="w-16 h-16 mb-4" />
                      <h3 className="text-xl font-semibold">Stream is Off</h3>
                      <p className="text-center">
                        Press the "Start Live Feed" button to begin streaming from backend.
                      </p>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex gap-4">
                  <Button
                    className="w-full text-white"
                    style={{ backgroundColor: "hsl(var(--accent))" }}
                    onClick={handleToggleStream}
                    disabled={isStartingStream}
                  >
                    {isStartingStream ? (
                      <Loader2 className="mr-2 animate-spin" />
                    ) : isLive ? (
                      <VideoOff className="mr-2" />
                    ) : (
                      <Play className="mr-2" />
                    )}
                    {isStartingStream
                      ? "Starting..."
                      : isLive
                      ? "Stop Live Feed"
                      : "Start Live Feed"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </main>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
