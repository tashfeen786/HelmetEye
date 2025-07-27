
"use client";

import { useState, useCallback, useRef } from "react";
import Image from "next/image";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, Loader2, X } from "lucide-react";

interface DetectionViewerProps {
  onDetect: () => void;
  detections: {
    id: string;
    box: [number, number, number, number]; // [x, y, width, height] in %
    hasHelmet: boolean;
  }[];
  onReset?: () => void;
}

export function DetectionViewer({ onDetect, detections, onReset }: DetectionViewerProps) {
  const [isDetecting, setIsDetecting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback((files: FileList | null) => {
    if (files && files[0]) {
      const file = files[0];
       if (previewUrl) {
          URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(URL.createObjectURL(file));
      if(onReset && detections.length > 0) {
        onReset();
      }
    }
  }, [previewUrl, detections, onReset]);

  const handleDetectClick = async () => {
    setIsDetecting(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    onDetect();
    setIsDetecting(false);
  };
  
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    handleFileChange(e.dataTransfer.files);
  }, [handleFileChange]);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }
  
  const handleReset = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(null);
    if(fileInputRef.current) {
        fileInputRef.current.value = "";
    }
    if (onReset) {
      onReset();
    }
  };


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
       <CardHeader>
          <CardTitle>Detection Viewer</CardTitle>
          <CardDescription>Upload an image or video to start detecting helmets.</CardDescription>
       </CardHeader>
      <CardContent className="p-4 md:p-6 flex flex-col gap-4">
        <div className="relative aspect-video w-full bg-muted rounded-lg overflow-hidden group" onDragOver={handleDragOver} onDrop={handleDrop}>
          {previewUrl ? (
            <Image
              src={previewUrl}
              alt="Uploaded content preview"
              layout="fill"
              objectFit="cover"
              className="transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-800/50">
                <div 
                    className="flex flex-col items-center justify-center w-full h-full text-center"
                    onClick={() => fileInputRef.current?.click()}
                 >
                   <div
                    className="flex flex-col items-center justify-center w-5/6 h-5/6 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-transparent hover:bg-gray-400/20"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-muted-foreground">
                      <UploadCloud className="w-10 h-10 mb-3" />
                      <p className="mb-2 text-sm"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                      <p className="text-xs">MP4, WEBM, or JPG</p>
                    </div>
                  </div>
                </div>
            </div>
          )}
          {detections.map((d) => (
            <BoundingBox key={d.id} box={d.box} hasHelmet={d.hasHelmet} />
          ))}
          <input ref={fileInputRef} id="dropzone-file" type="file" className="hidden" onChange={(e) => handleFileChange(e.target.files)} accept="video/*,image/*" />
          {previewUrl && (
             <Button variant="ghost" size="icon" className="absolute top-2 right-2 bg-black/50 hover:bg-black/70 text-white" onClick={handleReset}>
                <X className="w-5 h-5"/>
                <span className="sr-only">Clear media</span>
            </Button>
          )}
        </div>
        <div className="flex flex-col sm:flex-row gap-4">
            <Button onClick={() => fileInputRef.current?.click()} variant="outline" className="flex-1">
                <UploadCloud className="mr-2 h-4 w-4" />
                {previewUrl ? 'Change File' : 'Upload Image/Video'}
            </Button>
            <Button
                onClick={handleDetectClick}
                disabled={!previewUrl || isDetecting || detections.length > 0}
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
