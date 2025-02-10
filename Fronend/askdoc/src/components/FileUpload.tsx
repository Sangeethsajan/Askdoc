import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card } from "@/components/ui/card";

interface FileUploadProps {
  onUploadSuccess: () => void;
  userId: string;
}

const FileUpload = ({ onUploadSuccess, userId }: FileUploadProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(20);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length + files.length > 5) {
        alert("Maximum 5 files allowed");
        return;
      }
      setFiles((prev) => [...prev, ...acceptedFiles]);
    },
    [files]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
    },
    maxFiles: 5,
  });

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });
    formData.append("user_id", userId);

    try {
      const response = await fetch("http://localhost:8000/chat/load_docs/", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Upload failed");
      setProgress(50);
      setFiles([]);
      onUploadSuccess();
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
      setProgress(100);
    }
  };

  return (
    <Card className="max-w-2xl mx-auto mt-8 p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-primary bg-primary/5" : "hover:border-primary"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="h-8 w-8 mx-auto mb-4" />
        <p className="text-lg font-medium">
          {isDragActive ? "Drop the files here" : "Drag & drop PDF files here"}
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          or click to select files (maximum 5 PDFs)
        </p>
      </div>

      {files.length > 0 && (
        <div className="mt-4 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 border rounded"
            >
              <span className="truncate flex-1">{file.name}</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFile(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}

          {uploading ? (
            <Progress value={progress} className="mt-4" />
          ) : (
            <Button
              className="w-full mt-4"
              onClick={uploadFiles}
              disabled={files.length === 0}
            >
              Upload {files.length} {files.length === 1 ? "File" : "Files"}
            </Button>
          )}
        </div>
      )}
    </Card>
  );
};

export default FileUpload;
