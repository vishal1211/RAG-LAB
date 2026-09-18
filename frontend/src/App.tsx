import { useEffect, useRef, useState } from "react";

type Source = {
  filename: string | null;
  page: number | null;
  content: string;
  distance: number;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a PDF file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_BASE_URL}/upload/file`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setMessage(data.detail ?? "Upload failed.");
        return;
      }

      if (data.duplicate) {
        setMessage(`${data.filename} already exists.`);
      } else {
        setMessage(
          `${data.filename} uploaded successfully.`
        );
      }
    } catch {
      setMessage("Unable to connect to the backend.");
    }
  };
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  const askQuestion = async () => {
    if (!query.trim() || isLoading) {
      return;
    }

    setIsLoading(true);

    const currentQuery = query;

    setQuery("");

    const userMessage: ChatMessage = {
      role: "user",
      content: currentQuery,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/upload/search`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: currentQuery,
            session_id: sessionId,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Failed to get an answer."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources ?? [],
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Something went wrong.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main>
      <h1>RAG Lab</h1>

      <section>
        <h2>Upload PDF</h2>

        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => {
            const selectedFile =
              event.target.files?.[0] ?? null;

            setFile(selectedFile);
          }}
        />

        <button onClick={uploadFile}>
          Upload
        </button>

        <p>{message}</p>
      </section>

      <section>
        <h2>Ask your document</h2>

        <input
          type="text"
          value={query}
          placeholder="Ask a question..."
          disabled={isLoading}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !isLoading) {
              askQuestion();
            }
          }}
        />

        <button
          onClick={askQuestion}
          disabled={isLoading || !query.trim()}
        >
          {isLoading ? "Thinking..." : "Ask"}
        </button>

        <div>
          {messages.map((message, index) => (
            <div key={index}>
              <strong>
                {message.role === "user" ? "You" : "Assistant"}
              </strong>

              <p>{message.content}</p>

              {message.sources && message.sources.length > 0 && (
                <div>
                  <strong>Sources</strong>

                  {message.sources.map((source, sourceIndex) => (
                    <div key={sourceIndex}>
                      <p>
                        {source.filename}
                        {source.page !== null &&
                          ` — Page ${source.page}`}
                      </p>

                      <p>{source.content}</p>

                      <small>
                        Distance: {source.distance.toFixed(4)}
                      </small>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </section>
    </main>
  );
}

export default App;