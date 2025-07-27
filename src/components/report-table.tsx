
"use client"

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Calendar as CalendarIcon } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { cn } from "@/lib/utils";

interface ReportTableProps {
  history: {
    date: string;
    time: string;
    location:string;
    helmeted: number;
    unhelmeted: number;
    numberPlate?: string;
  }[];
}

export function ReportTable({ history }: ReportTableProps) {
  const [date, setDate] = useState<Date>();

  const filteredHistory = history.filter(item => {
    if (!date) return true;
    return new Date(item.date).toDateString() === date.toDateString();
  });

  const handleExport = () => {
    const headers = ["Date", "Time", "Location", "Number Plate", "Helmeted", "No Helmet", "Compliance (%)"];
    const csvRows = [headers.join(",")];

    filteredHistory.forEach(item => {
        const total = item.helmeted + item.unhelmeted;
        const compliance = total > 0 ? ((item.helmeted / total) * 100).toFixed(1) : "0.0";
        const row = [
            format(new Date(item.date), "yyyy-MM-dd"),
            item.time,
            `"${item.location.replace(/"/g, '""')}"`, // Handle commas in location
            item.numberPlate || "N/A",
            item.helmeted,
            item.unhelmeted,
            compliance
        ];
        csvRows.push(row.join(","));
    });

    const csvString = csvRows.join("\n");
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "helmet-detection-report.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <Card className="shadow-md">
      <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
            <CardTitle>Detection History</CardTitle>
            <CardDescription>A log of all past detection sessions.</CardDescription>
        </div>
        <div className="flex items-center gap-2 mt-4 md:mt-0">
            <Popover>
                <PopoverTrigger asChild>
                    <Button
                        variant={"outline"}
                        className={cn(
                            "w-full md:w-[280px] justify-start text-left font-normal",
                            !date && "text-muted-foreground"
                        )}
                    >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : <span>Pick a date to filter</span>}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                    <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    initialFocus
                    />
                </PopoverContent>
            </Popover>
            <Button variant="outline" onClick={handleExport}>
                <Download className="mr-2 h-4 w-4" />
                Export
            </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Number Plate</TableHead>
                <TableHead className="text-center">Helmeted</TableHead>
                <TableHead className="text-center">No Helmet</TableHead>
                <TableHead className="text-center">Compliance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredHistory.length > 0 && filteredHistory.map((item, index) => {
                const total = item.helmeted + item.unhelmeted;
                const compliance = total > 0 ? ((item.helmeted / total) * 100).toFixed(1) : "0.0";
                return (
                  <TableRow key={index}>
                    <TableCell className="font-medium whitespace-nowrap">{format(new Date(item.date), "PPP")}</TableCell>
                    <TableCell>{item.time}</TableCell>
                    <TableCell>{item.location}</TableCell>
                    <TableCell className="font-mono">{item.numberPlate || 'N/A'}</TableCell>
                    <TableCell className="text-center text-green-600 font-medium">{item.helmeted}</TableCell>
                    <TableCell className="text-center text-red-600 font-medium">{item.unhelmeted}</TableCell>
                    <TableCell className="text-center font-semibold">{compliance}%</TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </div>
        {filteredHistory.length === 0 && (
          <div className="text-center py-10 text-muted-foreground">
            No records found for the selected date.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
