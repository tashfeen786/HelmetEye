"use client";

import { useState, useCallback, useRef } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud, Loader2, X } from "lucide-react";

export function DetectionViewer() {
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [isVideo, setIsVideo] = useState(false);
  const [processedUrl, setProcessedUrl] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = useCallback((files: FileList | null) => {
    if (!files || !files[0]) return;
    const file = files[0];

    if (fileUrl) URL.revokeObjectURL(fileUrl);
    if (processedUrl) URL.revokeObjectURL(processedUrl);

    const url = URL.createObjectURL(file);
    setFileUrl(url);
    setProcessedUrl(null);
    setIsVideo(file.type.startsWith("video/"));
  }, [fileUrl, processedUrl]);

  const handleDetectClick = async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      alert("Please upload a file first.");
      return;
    }

    setIsDetecting(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const endpoint = isVideo ? "/api/detect_video" : "/api/detect_helmet";

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errMsg = await response.text();
        throw new Error(`Server error: ${errMsg}`);
      }

      const data = await response.json();

      if (isVideo && data.processedVideoUrl) {
        setProcessedUrl(`http://localhost:8000${data.processedVideoUrl}`);
      } else if (!isVideo && data.data?.processedImageUrl) {
        setProcessedUrl(`http://localhost:8000${data.data.processedImageUrl}`);
      }
    } catch (err) {
      console.error(err);
      alert("Detection failed. See console for details.");
    } finally {
      setIsDetecting(false);
    }
  };

  const handleReset = () => {
    if (fileUrl) URL.revokeObjectURL(fileUrl);
    if (processedUrl) URL.revokeObjectURL(processedUrl);
    setFileUrl(null);
    setProcessedUrl(null);
    setIsVideo(false);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const displayedUrl = processedUrl || fileUrl;

  return (
    <Card className="h-full shadow-md">
      <CardHeader>
        <CardTitle>Detection Viewer</CardTitle>
        <CardDescription>
          Upload an image or video. Detection only works for images or videos uploaded.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <div
          className="relative aspect-video w-full bg-gray-100 rounded-lg overflow-hidden cursor-pointer"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            handleFileChange(e.dataTransfer.files);
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          {displayedUrl ? (
            isVideo ? (
              <video
                src={displayedUrl}
                className="absolute inset-0 w-full h-full object-contain"
                controls
              />
            ) : (
              <img
                src={displayedUrl}
                alt="Preview"
                className="absolute inset-0 w-full h-full object-contain"
              />
            )
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <UploadCloud className="w-10 h-10 mx-auto mb-2" />
                <p className="text-sm font-semibold">Click to upload or drag & drop</p>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept="image/*,video/*"
            onChange={(e) => handleFileChange(e.target.files)}
          />

          {displayedUrl && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2 bg-black/50 text-white hover:bg-black/70"
              onClick={handleReset}
            >
              <X className="w-5 h-5" />
              <span className="sr-only">Clear</span>
            </Button>
          )}
        </div>

        <div className="flex gap-4">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => fileInputRef.current?.click()}
          >
            <UploadCloud className="mr-2 w-4 h-4" />
            {fileUrl ? "Change File" : "Upload File"}
          </Button>
          <Button
            className="flex-1 text-white"
            onClick={handleDetectClick}
            disabled={!fileUrl || isDetecting}
            style={{ backgroundColor: "hsl(var(--accent))" }}
          >
            {isDetecting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isDetecting ? "Detecting..." : "Run Detection"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
