
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
import { LayoutGrid, History, Video } from "lucide-react";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";
import Link from 'next/link';
import { ReportTable } from "@/components/report-table";
import { Button } from "@/components/ui/button";
import { Bell } from "lucide-react";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { type DetailedDetection } from "@/components/detailed-report-view";

const MOCK_HISTORY_DATA: DetailedDetection[] = [
    { id: 'evt-001', date: "2024-07-28", time: "14:32", location: "Main St & 1st Ave", numberPlate: "B-123-XYZ", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-002', date: "2024-07-28", time: "14:31", location: "Main St & 1st Ave", numberPlate: "C-456-ABC", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-003', date: "2024-07-28", time: "14:30", location: "Main St & 1st Ave", numberPlate: "A-789-PQR", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-004', date: "2024-07-27", time: "09:17", location: "Oak Rd & Pine Ln", numberPlate: "D-101-LMN", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-005', date: "2024-07-27", time: "09:16", location: "Oak Rd & Pine Ln", numberPlate: "E-202-JKL", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-006', date: "2024-07-27", time: "09:15", location: "Oak Rd & Pine Ln", numberPlate: "F-303-GHI", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-007', date: "2024-07-26", time: "17:45", location: "Central Plaza", numberPlate: "G-404-DEF", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-008', date: "2024-07-25", time: "12:05", location: "Highway 101", numberPlate: "H-505-UVW", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-009', date: "2024-07-25", time: "12:00", location: "Highway 101", numberPlate: "I-606-RST", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-010', date: "2024-07-24", time: "18:20", location: "City Bridge", numberPlate: "J-707-OPQ", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-011', date: "2024-07-23", time: "11:00", location: "Downtown Crossing", numberPlate: "K-808-MNO", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-012', date: "2024-07-22", time: "16:50", location: "Industrial Park", numberPlate: "L-909-IJK", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
];


export default function ReportsPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
        setIsLoading(false);
    }, 1500); // Simulate loading delay
    return () => clearTimeout(timer);
  }, []);

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
                <header className="flex items-center justify-between mb-6">
                    <Skeleton className="h-10 w-48" />
                    <div className="flex items-center gap-4">
                        <Skeleton className="h-10 w-10 rounded-full" />
                        <Skeleton className="h-10 w-10 rounded-full" />
                    </div>
                </header>
                 <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <Skeleton className="h-8 w-64" />
                            <Skeleton className="h-4 w-96 mt-2" />
                        </div>
                        <div className="flex items-center gap-2">
                            <Skeleton className="h-10 w-48" />
                            <Skeleton className="h-10 w-24" />
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2">
                            {[...Array(7)].map((_, i) => (
                                <div key={i} className="flex items-center p-4 rounded-lg">
                                    <Skeleton className="h-6 flex-1" />
                                    <Skeleton className="h-6 flex-1 ml-4" />
                                    <Skeleton className="h-6 flex-1 ml-4" />
                                    <Skeleton className="h-6 flex-1 ml-4" />
                                    <Skeleton className="h-6 flex-1 ml-4" />
                                </div>
                            ))}
                        </div>
                    </CardContent>
                 </Card>
            </div>
        </div>
    )
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
                <SidebarMenuButton>
                    <Video />
                    <span className="group-data-[collapsible=icon]:hidden">Live Feed</span>
                </SidebarMenuButton>
               </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link href="/reports" className="w-full">
                <SidebarMenuButton isActive>
                  <History />
                  <span className="group-data-[collapsible=icon]:hidden">Reports</span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarContent>
      </Sidebar>
      <SidebarInset>
         <div className="flex flex-col min-h-svh bg-muted/40">
             <header className="sticky top-0 z-30 flex items-center h-16 px-4 bg-background/95 backdrop-blur-sm border-b gap-4">
                <SidebarTrigger className="md:hidden" />
                <h1 className="text-xl font-semibold tracking-tight">Reports</h1>
                <div className="ml-auto flex items-center gap-4">
                    <Button variant="ghost" size="icon">
                        <Bell className="h-5 w-5"/>
                        <span className="sr-only">Notifications</span>
                    </Button>
                    <Avatar>
                        <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
                        <AvatarFallback>TA</AvatarFallback>
                    </Avatar>
                </div>
            </header>
            <main className="flex-1 p-4 md:p-6 lg:p-8">
                <ReportTable history={MOCK_HISTORY_DATA} />
            </main>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
