"use client";

import { useState } from "react";
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
import { LayoutGrid, History } from "lucide-react";
import Dashboard from "@/components/dashboard";
import { HelmetEyeLogo } from "@/components/helmet-eye-logo";

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
  history: [
    { date: "2024-07-28", time: "14:30", location: "Main St & 1st Ave", helmeted: 78, unhelmeted: 22 },
    { date: "2024-07-27", time: "09:15", location: "Oak Rd & Pine Ln", helmeted: 62, unhelmeted: 38 },
    { date: "2024-07-26", time: "17:45", location: "Central Plaza", helmeted: 91, unhelmeted: 9 },
    { date: "2024-07-25", time: "12:00", location: "Highway 101", helmeted: 120, unhelmeted: 15 },
    { date: "2024-07-24", time: "18:20", location: "City Bridge", helmeted: 55, unhelmeted: 3 },
  ],
};

export default function Home() {
  const [detectionData, setDetectionData] = useState<any>(null);
  
  const handleDetection = () => {
    // In a real app, this would come from an API call
    setDetectionData(MOCK_DETECTION_DATA);
  };

  const handleReset = () => {
    setDetectionData(null);
  }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader>
          <div className="flex items-center gap-2 p-2" onClick={handleReset} role="button">
            <HelmetEyeLogo className="w-8 h-8 text-primary" />
            <span className="text-lg font-semibold group-data-[collapsible=icon]:hidden">HelmetEye</span>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton isActive>
                <LayoutGrid />
                <span className="group-data-[collapsible=icon]:hidden">Dashboard</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton>
                <History />
                <span className="group-data-[collapsible=icon]:hidden">History</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarContent>
      </Sidebar>
      <SidebarInset>
        <Dashboard 
          onDetect={handleDetection}
          data={detectionData}
        />
      </SidebarInset>
    </SidebarProvider>
  );
}
