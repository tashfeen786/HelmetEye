
"use client"

import Image from "next/image";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export interface DetailedDetection {
  id: string;
  date: string;
  time: string;
  location: string;
  numberPlate: string;
  hasHelmet: boolean;
  imageUrl: string;
}

interface DetailedReportViewProps {
  detections: DetailedDetection[];
}

export function DetailedReportView({ detections }: DetailedReportViewProps) {
  if (detections.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        No detailed records found for the selected date.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Image</TableHead>
            <TableHead>Time</TableHead>
            <TableHead>Number Plate</TableHead>
            <TableHead>Location</TableHead>
            <TableHead className="text-center">Helmet Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {detections.map((detection) => (
            <TableRow key={detection.id}>
              <TableCell>
                <Image
                  src={detection.imageUrl}
                  alt={`Detection at ${detection.time}`}
                  width={150}
                  height={100}
                  className="rounded-md object-cover"
                  data-ai-hint="detection vehicle"
                />
              </TableCell>
              <TableCell className="font-medium">{detection.time}</TableCell>
              <TableCell>{detection.numberPlate}</TableCell>
              <TableCell>{detection.location}</TableCell>
              <TableCell className="text-center">
                <Badge variant={detection.hasHelmet ? "default" : "destructive"} className={detection.hasHelmet ? "bg-green-500" : "bg-red-500"}>
                  {detection.hasHelmet ? "Helmet" : "No Helmet"}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
