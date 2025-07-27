
"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DetectionViewer } from "@/components/detection-viewer";
import { SummaryPanel } from "@/components/summary-panel";
import { ReportTable } from "@/components/report-table";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Bell, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DashboardProps {
  onDetect: () => void;
  onReset: () => void;
  data: {
    helmetedCount: number;
    unhelmetedCount: number;
    totalCount: number;
    detections: any[];
    history: any[];
  } | null;
}

export default function Dashboard({ onDetect, data, onReset }: DashboardProps) {
  return (
    <div className="flex flex-col min-h-svh bg-muted/40">
      <header className="sticky top-0 z-30 flex items-center h-16 px-4 bg-background/95 backdrop-blur-sm border-b gap-4">
        <SidebarTrigger className="md:hidden" />
        <h1 className="text-xl font-semibold tracking-tight">Dashboard</h1>
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
        {!data ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
             <Card className="w-full max-w-4xl shadow-lg animate-in fade-in zoom-in-95">
              <CardHeader>
                <CardTitle className="text-3xl font-headline font-bold tracking-tight">Welcome to your Dashboard</CardTitle>
                <CardDescription className="text-lg text-muted-foreground">
                  Your AI-powered solution for monitoring helmet safety. Upload an image or video to begin.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DetectionViewer onDetect={onDetect} detections={[]} />
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3 animate-in fade-in">
            <div className="lg:col-span-2 space-y-6">
              <DetectionViewer onDetect={onDetect} detections={data.detections} onReset={onReset} />
              <ReportTable history={data.history} />
            </div>
            <div className="lg:col-span-1 row-start-1 lg:row-start-auto">
              <SummaryPanel
                helmetedCount={data.helmetedCount}
                unhelmetedCount={data.unhelmetedCount}
                totalCount={data.totalCount}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
