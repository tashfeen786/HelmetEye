
"use client";

import { useState, useRef, useEffect, useCallback } from "react";
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
import { LayoutGrid, History, Video, CameraOff, VideoOff, Play } from "lucide-react";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";


export default function LiveFeedPage() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
    const [isLive, setIsLive] = useState(false);
    const { toast } = useToast();

    const stopStream = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
            if(videoRef.current) videoRef.current.srcObject = null;
            setIsLive(false);
        }
    }, []);

    const startStream = useCallback(async () => {
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({video: true});
                setHasCameraPermission(true);
                streamRef.current = stream;

                if (videoRef.current) {
                  videoRef.current.srcObject = stream;
                }
                setIsLive(true);
            } else {
                 setHasCameraPermission(false);
                 setIsLive(false);
            }
          } catch (error) {
            console.error('Error accessing camera:', error);
            setHasCameraPermission(false);
            setIsLive(false);
            toast({
              variant: 'destructive',
              title: 'Camera Access Denied',
              description: 'Please enable camera permissions in your browser settings to use this app.',
            });
          }
    }, [toast]);
    
    useEffect(() => {
        // Initial permission check
        navigator.permissions.query({ name: 'camera' as PermissionName }).then(res => {
            if (res.state === 'granted') {
                setHasCameraPermission(true);
            } else if (res.state === 'denied') {
                setHasCameraPermission(false);
            } else {
                setHasCameraPermission(null);
            }
        });

        // Cleanup stream on component unmount
        return () => {
            stopStream();
        }
    }, [stopStream]);

    const handleToggleStream = () => {
        if(isLive) {
            stopStream();
        } else {
            startStream();
        }
    }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <Link href="/" className="flex items-center gap-2 p-2" role="button">
            <HelmetEyeLogo className="w-8 h-8 text-primary" />
            <span className="text-lg font-semibold group-data-[collapsible=icon]:hidden">HelmetEye</span>
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
                        <CardTitle>Live Camera Feed</CardTitle>
                        <CardDescription>Real-time video stream for helmet detection.</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="relative aspect-video w-full bg-muted rounded-lg overflow-hidden">
                           <video ref={videoRef} className="w-full h-full object-cover" autoPlay muted playsInline />
                           {!isLive && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 text-white p-4">
                                    <CameraOff className="w-16 h-16 mb-4"/>
                                    <h3 className="text-xl font-semibold">{hasCameraPermission === false ? 'Camera Access Denied' : 'Camera is Off'}</h3>
                                    <p className="text-center">{hasCameraPermission === false ? 'Please enable camera permissions in your browser.' : 'Press the "Start Live Feed" button to begin.'}</p>
                                </div>
                            )}
                        </div>
                         <div className="mt-4 flex gap-4">
                            <Button className="w-full text-white" style={{backgroundColor: 'hsl(var(--accent))'}} onClick={handleToggleStream}>
                                {isLive ? <VideoOff className="mr-2" /> : <Play className="mr-2"/>}
                                {isLive ? 'Stop Live Feed' : 'Start Live Feed'}
                            </Button>
                        </div>

                         {hasCameraPermission === false && (
                            <Alert variant="destructive" className="mt-4">
                                <AlertTitle>Camera Access Required</AlertTitle>
                                <AlertDescription>
                                    Please allow camera access in your browser settings and refresh the page to use this feature.
                                </AlertDescription>
                           </Alert>
                         )}
                    </CardContent>
                </Card>
            </main>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
