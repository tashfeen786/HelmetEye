
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
import { Download, Calendar as CalendarIcon, X } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { DetailedReportView, type DetailedDetection } from "./detailed-report-view";

interface ReportTableProps {
  history: DetailedDetection[];
}

interface DailySummary {
  date: string;
  rawDate: Date;
  location: string;
  helmeted: number;
  unhelmeted: number;
  total: number;
}

export function ReportTable({ history }: ReportTableProps) {
  const [date, setDate] = useState<Date>();

  const dailySummaries = history.reduce<Record<string, DailySummary>>((acc, item) => {
    const itemDate = new Date(item.date);
    const dateStr = format(itemDate, "yyyy-MM-dd");
    if (!acc[dateStr]) {
      acc[dateStr] = {
        date: format(itemDate, "PPP"),
        rawDate: itemDate,
        location: item.location, // simplified for summary
        helmeted: 0,
        unhelmeted: 0,
        total: 0,
      };
    }
    if (item.hasHelmet) {
      acc[dateStr].helmeted++;
    } else {
      acc[dateStr].unhelmeted++;
    }
    acc[dateStr].total++;
    return acc;
  }, {});

  const filteredHistory = date
    ? history.filter(item => new Date(item.date).toDateString() === date.toDateString())
    : [];

  const handleExport = () => {
    const dataToExport = date ? filteredHistory : Object.values(dailySummaries);
    const headers = date
      ? ["ID", "Date", "Time", "Location", "Number Plate", "Helmet Status", "Image URL"]
      : ["Date", "Location", "Helmeted", "No Helmet", "Compliance (%)"];

    const csvRows = [headers.join(",")];

    if (date) {
        filteredHistory.forEach(item => {
            const row = [
                item.id,
                format(new Date(item.date), "yyyy-MM-dd"),
                item.time,
                `"${item.location.replace(/"/g, '""')}"`,
                item.numberPlate,
                item.hasHelmet ? 'Helmet' : 'No Helmet',
                item.imageUrl
            ];
            csvRows.push(row.join(","));
        });
    } else {
        Object.values(dailySummaries).forEach(item => {
            const compliance = item.total > 0 ? ((item.helmeted / item.total) * 100).toFixed(1) : "0.0";
            const row = [
                item.date,
                `"${item.location.replace(/"/g, '""')}"`,
                item.helmeted,
                item.unhelmeted,
                compliance
            ];
            csvRows.push(row.join(","));
        });
    }
    

    const csvString = csvRows.join("\n");
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `helmet-detection-report${date ? `-${format(date, "yyyy-MM-dd")}`: ''}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };
  
  const handleDateSelect = (selectedDate?: Date) => {
    setDate(selectedDate);
  }

  return (
    <Card className="shadow-md">
      <CardHeader className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
            <CardTitle>Detection History</CardTitle>
            <CardDescription>{date ? `Detailed report for ${format(date, "PPP")}` : 'Summary of all past detection sessions.'}</CardDescription>
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
                    {date ? format(date, "PPP") : <span>Pick a date to view details</span>}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                    <Calendar
                        mode="single"
                        selected={date}
                        onSelect={handleDateSelect}
                        initialFocus
                    />
                </PopoverContent>
            </Popover>
             {date && (
                <Button variant="ghost" size="icon" onClick={() => setDate(undefined)}>
                    <X className="h-4 w-4" />
                    <span className="sr-only">Clear date filter</span>
                </Button>
            )}
            <Button variant="outline" onClick={handleExport}>
                <Download className="mr-2 h-4 w-4" />
                Export
            </Button>
        </div>
      </CardHeader>
      <CardContent>
        {date ? (
            <DetailedReportView detections={filteredHistory} />
        ) : (
            <>
                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                        <TableRow>
                            <TableHead>Date</TableHead>
                            <TableHead>Location</TableHead>
                            <TableHead className="text-center">Helmeted</TableHead>
                            <TableHead className="text-center">No Helmet</TableHead>
                            <TableHead className="text-center">Compliance</TableHead>
                        </TableRow>
                        </TableHeader>
                        <TableBody>
                        {Object.values(dailySummaries).map((item, index) => {
                            const compliance = item.total > 0 ? ((item.helmeted / item.total) * 100).toFixed(1) : "0.0";
                            return (
                            <TableRow key={index} className="cursor-pointer" onClick={() => handleDateSelect(item.rawDate)}>
                                <TableCell className="font-medium whitespace-nowrap">{item.date}</TableCell>
                                <TableCell>{item.location}</TableCell>
                                <TableCell className="text-center text-green-600 font-medium">{item.helmeted}</TableCell>
                                <TableCell className="text-center text-red-600 font-medium">{item.unhelmeted}</TableCell>
                                <TableCell className="text-center font-semibold">{compliance}%</TableCell>
                            </TableRow>
                            )
                        })}
                        </TableBody>
                    </Table>
                </div>
                {Object.keys(dailySummaries).length === 0 && (
                <div className="text-center py-10 text-muted-foreground">
                    No records found.
                </div>
                )}
            </>
        )}
      </CardContent>
    </Card>
  );
}
