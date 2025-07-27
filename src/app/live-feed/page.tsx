
"use client";

import { useState, useRef, useEffect } from "react";
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
import { LayoutGrid, History, Video, CameraOff } from "lucide-react";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";


export default function LiveFeedPage() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
    const { toast } = useToast();

    useEffect(() => {
        const getCameraPermission = async () => {
          try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({video: true});
                setHasCameraPermission(true);

                if (videoRef.current) {
                  videoRef.current.srcObject = stream;
                }
            } else {
                 setHasCameraPermission(false);
            }
          } catch (error) {
            console.error('Error accessing camera:', error);
            setHasCameraPermission(false);
            toast({
              variant: 'destructive',
              title: 'Camera Access Denied',
              description: 'Please enable camera permissions in your browser settings to use this app.',
            });
          }
        };

        getCameraPermission();
        
        return () => {
            if(videoRef.current && videoRef.current.srcObject) {
                const stream = videoRef.current.srcObject as MediaStream;
                stream.getTracks().forEach(track => track.stop());
            }
        }
    }, [toast]);

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
                <Link href="/dashboard" className="w-full">
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
                           {hasCameraPermission === false && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 text-white p-4">
                                    <CameraOff className="w-16 h-16 mb-4"/>
                                    <h3 className="text-xl font-semibold">Camera Access Denied</h3>
                                    <p className="text-center">Please enable camera permissions in your browser to view the live feed.</p>
                                </div>
                            )}
                             {hasCameraPermission === null && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 text-white p-4">
                                    <p>Requesting camera permission...</p>
                                </div>
                            )}
                        </div>
                         {hasCameraPermission === true && (
                            <div className="mt-4">
                                <Button className="w-full text-white" style={{backgroundColor: 'hsl(var(--accent))'}}>Start Live Detection</Button>
                            </div>
                        )}
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

    