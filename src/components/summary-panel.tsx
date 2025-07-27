"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Lightbulb, Loader2, Shield, ShieldOff } from "lucide-react";
import { suggestAlternativeAction, type SuggestAlternativeActionOutput } from "@/ai/flows/suggest-alternative-message";

interface SummaryPanelProps {
  helmetedCount: number;
  unhelmetedCount: number;
  totalCount: number;
}

const COLORS = ['hsl(var(--chart-3))', 'hsl(var(--chart-2))'];

export function SummaryPanel({ helmetedCount, unhelmetedCount, totalCount }: SummaryPanelProps) {
  const [suggestion, setSuggestion] = useState<SuggestAlternativeActionOutput | null>(null);
  const [isSuggesting, setIsSuggesting] = useState(false);
  
  const chartData = [
    { name: 'Helmeted', value: helmetedCount, fill: 'hsl(var(--chart-3))' },
    { name: 'No Helmet', value: unhelmetedCount, fill: 'hsl(var(--chart-2))' },
  ];

  const handleGetSuggestion = async () => {
    setIsSuggesting(true);
    setSuggestion(null);
    try {
      const result = await suggestAlternativeAction({ unhelmetedCount, totalCount });
      setSuggestion(result);
    } catch (error) {
      console.error("Failed to get suggestion:", error);
      setSuggestion({ suggestion: "Could not retrieve a suggestion at this time. Please try again later." });
    }
    setIsSuggesting(false);
  };

  return (
    <Card className="h-full flex flex-col shadow-md">
      <CardHeader>
        <CardTitle>Detection Summary</CardTitle>
        <CardDescription>Overview of the latest detection results.</CardDescription>
      </CardHeader>
      <CardContent className="flex-grow flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4 text-center">
            <Card className="bg-green-500/10 border-green-500/20">
                <CardHeader className="p-4">
                    <CardTitle className="flex items-center justify-center gap-2 text-green-600"><Shield/> Helmeted</CardTitle>
                    <CardDescription className="text-3xl font-bold text-foreground">{helmetedCount}</CardDescription>
                </CardHeader>
            </Card>
             <Card className="bg-red-500/10 border-red-500/20">
                <CardHeader className="p-4">
                    <CardTitle className="flex items-center justify-center gap-2 text-red-600"><ShieldOff/> No Helmet</CardTitle>
                    <CardDescription className="text-3xl font-bold text-foreground">{unhelmetedCount}</CardDescription>
                </CardHeader>
            </Card>
        </div>

        <div className="aspect-square w-full">
            <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                    <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5}>
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip contentStyle={{
                        background: 'hsl(var(--background))',
                        borderColor: 'hsl(var(--border))',
                        borderRadius: 'var(--radius)',
                    }}/>
                    <Legend />
                </PieChart>
            </ResponsiveContainer>
        </div>

        <div className="mt-auto flex flex-col gap-4">
            {suggestion && (
                <Card className="bg-primary/10 border-primary/20 animate-in fade-in">
                    <CardContent className="p-4">
                        <p className="text-sm text-primary">{suggestion.suggestion}</p>
                    </CardContent>
                </Card>
            )}
            <Button onClick={handleGetSuggestion} disabled={isSuggesting} className="w-full">
                {isSuggesting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                    <Lightbulb className="mr-2 h-4 w-4" />
                )}
                {isSuggesting ? 'Analyzing...' : 'Get AI Suggestion'}
            </Button>
        </div>
      </CardContent>
    </Card>
  );
}
