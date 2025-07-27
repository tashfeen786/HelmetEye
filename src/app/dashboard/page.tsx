
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
} from "@/components/ui/sidebar";
import { LayoutGrid, History, Video } from "lucide-react";
import Dashboard from "@/components/dashboard";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";
import Link from 'next/link';
import { Skeleton } from "@/components/ui/skeleton";
import { type DetailedDetection } from "@/components/detailed-report-view";

const MOCK_DETAILED_HISTORY: DetailedDetection[] = [
    { id: 'evt-001', date: "2024-07-28", time: "14:32", location: "Main St & 1st Ave", numberPlate: "B-123-XYZ", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-002', date: "2024-07-28", time: "14:31", location: "Main St & 1st Ave", numberPlate: "C-456-ABC", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-003', date: "2024-07-28", time: "14:30", location: "Main St & 1st Ave", numberPlate: "A-789-PQR", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-004', date: "2024-07-27", time: "09:17", location: "Oak Rd & Pine Ln", numberPlate: "D-101-LMN", hasHelmet: false, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-005', date: "2024-07-27", time: "09:16", location: "Oak Rd & Pine Ln", numberPlate: "E-202-JKL", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-006', date: "2024-07-27", time: "09:15", location: "Oak Rd & Pine Ln", numberPlate: "F-303-GHI", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
    { id: 'evt-007', date: "2024-07-26", time: "17:45", location: "Central Plaza", numberPlate: "G-404-DEF", hasHelmet: true, imageUrl: "https://placehold.co/150x100.png" },
];

// Mock data for detection results
const MOCK_DETECTION_DATA = {
  helmetedCount: 78,
  unhelmetedCount: 22,
  totalCount: 100,
  detections: [
    { id: 'det_1', box: [15, 20, 10, 12], hasHelmet: true },
    { id: 'det_2', box: [60, 30, 12, 15], hasHelmet: false },
    { id: 'det_3', box: [30, 50, 11, 13], hasHelmet: true },
    { id: 'det_4', box: [75, 65, 10, 12], hasHelmet: true },
  ],
  history: MOCK_DETAILED_HISTORY,
};

export default function DashboardPage() {
  const [detectionData, setDetectionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
        setIsLoading(false);
    }, 1500); // Simulate loading delay
    return () => clearTimeout(timer);
  }, []);
  
  const handleDetection = () => {
    // In a real app, this would come from an API call
    setDetectionData(MOCK_DETECTION_DATA);
  };

  const handleReset = () => {
    setDetectionData(null);
  }
  
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
                <div className="flex-1 p-8 space-y-6">
                    <Skeleton className="h-10 w-64 mb-4" />
                    <Skeleton className="w-full h-[400px]" />
                    <Skeleton className="w-full h-[200px]" />
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
                    <SidebarMenuButton isActive>
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
        <Dashboard 
          onDetect={handleDetection}
          data={detectionData}
          onReset={handleReset}
        />
      </SidebarInset>
    </SidebarProvider>
  );
}
