"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DetectionViewer } from "@/components/detection-viewer";
import { SummaryPanel } from "@/components/summary-panel";
import { ReportTable } from "@/components/report-table";
import { SidebarTrigger } from "@/components/ui/sidebar";

interface DashboardProps {
  onDetect: () => void;
  data: {
    helmetedCount: number;
    unhelmetedCount: number;
    totalCount: number;
    detections: any[];
    history: any[];
  } | null;
}

export default function Dashboard({ onDetect, data }: DashboardProps) {
  return (
    <div className="flex flex-col min-h-svh">
      <header className="sticky top-0 z-10 flex items-center h-16 px-4 bg-background/80 backdrop-blur-sm border-b gap-4">
        <SidebarTrigger className="md:hidden" />
        <h1 className="text-xl font-semibold">Dashboard</h1>
      </header>
      <main className="flex-1 p-4 md:p-6 lg:p-8">
        {!data ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
             <Card className="w-full max-w-4xl shadow-lg">
              <CardHeader>
                <CardTitle className="text-3xl font-headline font-bold tracking-tight">Welcome to HelmetEye</CardTitle>
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
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <DetectionViewer onDetect={onDetect} detections={data.detections} />
            </div>
            <div className="lg:col-span-1 row-start-1 lg:row-start-auto">
              <SummaryPanel
                helmetedCount={data.helmetedCount}
                unhelmetedCount={data.unhelmetedCount}
                totalCount={data.totalCount}
              />
            </div>
            <div className="lg:col-span-3">
              <ReportTable history={data.history} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
