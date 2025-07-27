"use client";

import { useState, useCallback } from "react";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, Loader2 } from "lucide-react";

interface DetectionViewerProps {
  onDetect: () => void;
  detections: {
    id: string;
    box: [number, number, number, number]; // [x, y, width, height] in %
    hasHelmet: boolean;
  }[];
}

export function DetectionViewer({ onDetect, detections }: DetectionViewerProps) {
  const [isDetecting, setIsDetecting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = useCallback((files: FileList | null) => {
    if (files && files[0]) {
      const file = files[0];
      if (previewUrl) {
          URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(URL.createObjectURL(file));
    }
  }, [previewUrl]);

  const handleDetectClick = async () => {
    setIsDetecting(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    onDetect();
    setIsDetecting(false);
  };
  
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    handleFileChange(e.dataTransfer.files);
  }, [handleFileChange]);

  const BoundingBox = ({ box, hasHelmet }: { box: [number, number, number, number]; hasHelmet: boolean }) => (
    <div
      className={`absolute border-2 ${hasHelmet ? 'border-green-500' : 'border-red-500'} rounded-md shadow-lg animate-in fade-in duration-500`}
      style={{
        left: `${box[0]}%`,
        top: `${box[1]}%`,
        width: `${box[2]}%`,
        height: `${box[3]}%`,
      }}
    >
      <span className={`absolute -top-6 left-0 text-xs font-bold px-1 rounded-sm ${hasHelmet ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
        {hasHelmet ? 'Helmet' : 'No Helmet'}
      </span>
    </div>
  );

  return (
    <Card className="h-full shadow-md">
      <CardContent className="p-4 md:p-6 flex flex-col gap-4">
        <div className="relative aspect-video w-full bg-muted rounded-lg overflow-hidden group">
          <Image
            src={previewUrl || "https://placehold.co/1280x720.png"}
            alt="Video feed placeholder"
            layout="fill"
            objectFit="cover"
            data-ai-hint="road traffic"
            className="transition-transform duration-300 group-hover:scale-105"
          />
          {detections.map((d) => (
            <BoundingBox key={d.id} box={d.box} hasHelmet={d.hasHelmet} />
          ))}
          {!previewUrl && (
             <div 
                className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 transition-all duration-300"
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                onClick={() => document.getElementById('dropzone-file')?.click()}
             >
               <div
                className="flex flex-col items-center justify-center w-5/6 h-5/6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-transparent hover:bg-gray-400/20"
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6 text-white">
                  <UploadCloud className="w-10 h-10 mb-3" />
                  <p className="mb-2 text-sm"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                  <p className="text-xs">MP4, WEBM, or JPG</p>
                </div>
                <input id="dropzone-file" type="file" className="hidden" onChange={(e) => handleFileChange(e.target.files)} accept="video/*,image/*" />
              </div>
            </div>
          )}
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
            <Button onClick={() => document.getElementById('dropzone-file')?.click()} variant="outline" className="flex-1">
                <UploadCloud className="mr-2 h-4 w-4" />
                {previewUrl ? 'Change File' : 'Upload Image/Video'}
            </Button>
            <Button
                onClick={handleDetectClick}
                disabled={!previewUrl || isDetecting}
                className="flex-1 text-white"
                style={{backgroundColor: 'hsl(var(--accent))'}}
            >
                {isDetecting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                {isDetecting ? 'Detecting...' : 'Run Detection'}
            </Button>
        </div>
      </CardContent>
    </Card>
  );
}
