import { Document } from "@/types";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Checkbox } from "@/components/ui/checkbox";

interface DocumentSelectorProps {
  documents: Document[];
  selectedDocuments: number[];
  onDocumentSelect: (ids: number[]) => void;
}

const DocumentSelector = ({
  documents,
  selectedDocuments,
  onDocumentSelect,
}: DocumentSelectorProps) => {
  const handleToggle = (docId: number) => {
    const newSelection = selectedDocuments.includes(docId)
      ? selectedDocuments.filter((id) => id !== docId)
      : [...selectedDocuments, docId];
    onDocumentSelect(newSelection);
  };

  return (
    <Card className="w-72 p-4">
      <div className="font-semibold">Select Documents</div>
      <div className="text-xs mb-4">
        You can select the documents to retrieve the answers from.
      </div>
      <ScrollArea className="h-[calc(100vh-20rem)]">
        <div className="space-y-4">
          {documents.map((doc) => (
            <div key={doc.id} className="flex items-top space-x-3">
              <Checkbox
                id={`doc-${doc.id}`}
                checked={selectedDocuments.includes(doc.id)}
                onCheckedChange={() => handleToggle(doc.id)}
              />
              <label
                htmlFor={`doc-${doc.id}`}
                className="text-sm leading-none cursor-pointer"
              >
                <div className="font-medium">{doc.filename}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {new Date(doc.created_at).toLocaleDateString()}
                </div>
              </label>
            </div>
          ))}
        </div>
      </ScrollArea>
    </Card>
  );
};

export default DocumentSelector;
