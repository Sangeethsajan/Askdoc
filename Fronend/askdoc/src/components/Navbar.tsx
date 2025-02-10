import { FileText, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  onStartOver: () => void;
  hasDocuments: boolean;
}

const Navbar = ({ onStartOver, hasDocuments }: NavbarProps) => {
  return (
    <nav className="border-b">
      <div className="flex h-16 items-center px-4 container mx-auto justify-between">
        <div className="flex items-center gap-2">
          <FileText className="h-7 w-7" />
          <span className="text-2xl font-semibold">AskDoc</span>
        </div>
        {hasDocuments && (
          <Button
            variant="outline"
            onClick={onStartOver}
            className="flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Start Over
          </Button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
