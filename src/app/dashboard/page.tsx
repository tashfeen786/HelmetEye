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
  // ... tumhara mock data
];

const MOCK_DETECTION_DATA = {
  // ... tumhara mock detection data
};

export default function DashboardPage() {
  const [detectionData, setDetectionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isMounted, setIsMounted] = useState(false); // 👈 add

  useEffect(() => {
    setIsMounted(true); // 👈 set mount state
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

const handleDetection = async (file: File) => {
  try {
    if (!file) {
      throw new Error("No file provided to detection API");
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://localhost:8000/api/detect_helmet", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errMsg = await response.text();
      throw new Error(`Network response was not ok: ${response.status} → ${errMsg}`);
    }

    const result = await response.json();
    setDetectionData(result.data);
  } catch (err) {
    console.error("Error fetching detection data:", err);
  }
};


  const handleReset = () => {
    setDetectionData(null);
  };

  // 👇 Prevent hydration error
  if (!isMounted) {
    return null; // ya <Skeleton /> bhi dikha sakte ho
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
                <SidebarMenuButton isActive>
                  <LayoutGrid />
                  <span className="group-data-[collapsible=icon]:hidden">
                    Dashboard
                  </span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link href="/live-feed" className="w-full">
                <SidebarMenuButton>
                  <Video />
                  <span className="group-data-[collapsible=icon]:hidden">
                    Live Feed
                  </span>
                </SidebarMenuButton>
              </Link>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <Link href="/reports" className="w-full">
                <SidebarMenuButton>
                  <History />
                  <span className="group-data-[collapsible=icon]:hidden">
                    Reports
                  </span>
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
