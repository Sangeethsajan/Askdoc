import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText } from "lucide-react";
import { StreamResponse } from "@/types";

interface SourceCardProps {
  sources: StreamResponse["sources"];
}

const SourceCard = ({ sources }: SourceCardProps) => {
  return (
    <Card className="w-full bg-muted/50 mt-2">
      <CardHeader className="p-4">
        <CardTitle className="text-sm flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Sources
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <ScrollArea className="h-[200px]">
          {sources?.map((source, idx) => (
            <div
              key={idx}
              className="mb-4 p-3 bg-background rounded-lg last:mb-0"
            >
              <div className="flex justify-between items-start mb-2">
                <span className="font-medium truncate">
                  {source.metadata.filename}
                </span>
                <span className="text-xs text-muted-foreground">
                  Page {source.metadata.page_number}
                </span>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-3">
                {source.metadata.content}
              </p>
            </div>
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default SourceCard;
