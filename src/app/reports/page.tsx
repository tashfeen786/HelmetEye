
"use client";

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


// Mock data for detection results
const MOCK_HISTORY_DATA = [
    { date: "2024-07-28", time: "14:30", location: "Main St & 1st Ave", helmeted: 78, unhelmeted: 22 },
    { date: "2024-07-27", time: "09:15", location: "Oak Rd & Pine Ln", helmeted: 62, unhelmeted: 38 },
    { date: "2024-07-26", time: "17:45", location: "Central Plaza", helmeted: 91, unhelmeted: 9 },
    { date: "2024-07-25", time: "12:00", location: "Highway 101", helmeted: 120, unhelmeted: 15 },
    { date: "2024-07-24", time: "18:20", location: "City Bridge", helmeted: 55, unhelmeted: 3 },
    { date: "2024-07-23", time: "11:00", location: "Downtown Crossing", helmeted: 88, unhelmeted: 12 },
    { date: "2024-07-22", time: "16:50", location: "Industrial Park", helmeted: 45, unhelmeted: 5 },
];

export default function ReportsPage() {

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
