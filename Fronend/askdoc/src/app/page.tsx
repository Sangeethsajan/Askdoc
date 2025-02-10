"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import FileUpload from "@/components/FileUpload";
import Chat from "@/components/Chat";
import { Document } from "@/types";
import { useUser } from "@/hooks/useUser";
import { Jumbotron, MiniJumbotron } from "@/components/Jumbotron";
import { makeAPIRequest } from "../services/apiservices";
export default function Home() {
  const { userId, isLoading } = useUser();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);

  const fetchDocuments = async (uid: string) => {
    const formData = new FormData();
    formData.append("user_id", uid);
    try {
      const response = await makeAPIRequest("chat/get_docs/", "POST", formData);
      /*const response = await fetch("http://localhost:8000/chat/get_docs/", {
        method: "POST",
        body: formData,
      });*/
      //if (!response.ok) throw new Error("Failed to fetch documents");
      const data = response;
      setDocuments(data);
      setSelectedDocuments(data.map((doc: Document) => doc.id));
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchDocuments(userId);
    }
  }, [userId]);

  const handleStartOver = async () => {
    if (!userId) return;

    try {
      // Delete all documents for the user
      const formData = new FormData();
      formData.append("user_id", userId);
      await makeAPIRequest("chat/delete_docs/", "POST", formData);
      /*
      await fetch("http://localhost:8000/chat/delete_docs/", {
        method: "POST",
        body: formData,
      });*/

      setDocuments([]);
      setSelectedDocuments([]);
    } catch (error) {
      console.error("Error during reset:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar
        onStartOver={handleStartOver}
        hasDocuments={documents.length > 0}
      />

      <main className="container mx-auto px-4 py-8">
        {documents.length === 0 ? (
          <>
            <Jumbotron />
            <FileUpload
              onUploadSuccess={() => userId && fetchDocuments(userId)}
              userId={userId!}
            />
          </>
        ) : (
          <>
            <MiniJumbotron />
            <Chat
              documents={documents}
              selectedDocuments={selectedDocuments}
              onDocumentSelect={setSelectedDocuments}
              userId={userId!}
            />
          </>
        )}
      </main>
    </div>
  );
}
