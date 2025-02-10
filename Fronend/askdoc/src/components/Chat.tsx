import { useEffect, useRef, useState } from "react";
import { ChatProps, Message, StreamResponse } from "@/types";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import DocumentSelector from "./DocumentSelector";
import { ScrollArea } from "@/components/ui/scroll-area";
import SourceCard from "./SourceCard";
import { Send } from "lucide-react";
import { makeStreamingAPIREquest } from "@/services/apiservices";
import TypingIndicator from "./TypingIndicator";
const Chat = ({
  documents,
  selectedDocuments,
  onDocumentSelect,
}: ChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    // Smooth scroll with a slight delay to ensure content is rendered
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  }, [messages, streamingContent]);
  useEffect(scrollToBottom, [messages, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || selectedDocuments.length === 0) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    let currentContent = ""; // Track content locally

    const formData = new FormData();
    formData.append("query", input);
    formData.append("document_list", JSON.stringify(selectedDocuments));

    try {
      /*
      const response = await fetch("http://localhost:8000/chat/ask/", {
        method: "POST",
        body: formData,
      });*/
      const response = await makeStreamingAPIREquest(
        "chat/ask/",
        "POST",
        formData
      );
      if (!response?.ok) throw new Error("Failed to get response");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data: StreamResponse = JSON.parse(line.slice(6));

              if (data.content) {
                currentContent += data.content;
                setStreamingContent(currentContent); // Update streaming content
              }

              if (data.sources) {
                // Add final message with complete content
                setMessages((prev) => [
                  ...prev,
                  {
                    role: "assistant",
                    content: currentContent,
                    sources: data.sources,
                  },
                ]);
                setStreamingContent(""); // Clear streaming content after message is added
              }
            } catch (e) {
              console.error("Error parsing chunk:", e);
            }
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="flex gap-4 h-[calc(100vh-16rem)] max-w-6xl mx-auto">
      <div className="flex-1 min-h-0">
        {" "}
        {/* Added min-h-0 to allow proper flex shrinking */}
        <Card className="h-full flex flex-col">
          <ScrollArea className="flex-1 p-4 h-[calc(100vh-22rem)]">
            {" "}
            {/* Fixed height calculation */}
            <div className="space-y-4 pb-4">
              {" "}
              {/* Added padding bottom for last message visibility */}
              {/* Completed Messages */}
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-4 animate-fade-in ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words">
                      {" "}
                      {/* Added break-words */}
                      {message.content}
                    </p>

                    {message.sources && message.sources.length > 0 && (
                      <SourceCard sources={message.sources} />
                    )}
                  </div>
                </div>
              ))}
              {/* Streaming Response with Typing Indicator */}
              {loading && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg p-4 bg-muted animate-fade-in">
                    {streamingContent ? (
                      <p className="whitespace-pre-wrap break-words">
                        {streamingContent}
                        <span className="inline-block w-1 h-4 ml-1 bg-current animate-pulse" />
                      </p>
                    ) : (
                      <TypingIndicator />
                    )}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          <div className="p-4 border-t mt-auto">
            {" "}
            {/* Changed to div with mt-auto */}
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  selectedDocuments.length === 0
                    ? "Please select at least one document"
                    : "Ask a question..."
                }
                disabled={loading || selectedDocuments.length === 0}
              />
              <Button
                type="submit"
                disabled={loading || selectedDocuments.length === 0}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        </Card>
      </div>

      <DocumentSelector
        documents={documents}
        selectedDocuments={selectedDocuments}
        onDocumentSelect={onDocumentSelect}
      />
    </div>
  );
};

export default Chat;
