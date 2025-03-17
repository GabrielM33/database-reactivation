"use client";

import { useState, useEffect, FormEvent } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Message {
  id: number;
  content: string;
  is_from_lead: boolean;
  sent_at: string;
  delivered: boolean;
}

interface ConversationDetail {
  conversation_id: number;
  lead_name: string;
  state: string;
  messages: Message[];
}

export default function ConversationDetailPage() {
  const params = useParams();
  const conversationId = params.id;

  const [conversation, setConversation] = useState<ConversationDetail | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchConversation();
  }, [conversationId]);

  const fetchConversation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/conversations/${conversationId}/messages`
      );
      const data = await response.json();

      if (!response.ok) {
        throw new Error(`Failed to fetch conversation: ${response.status}`);
      }

      if (!data || !data.conversation_id) {
        throw new Error(
          `Conversation with ID ${conversationId} not found. Please check the conversations list.`
        );
      }

      setConversation(data);
    } catch (err) {
      console.error("Error fetching conversation:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();

    if (!newMessage.trim() || !conversation) {
      return;
    }

    setSending(true);

    try {
      // Get lead ID from the API
      const conversationsResponse = await fetch(
        `http://localhost:8000/conversations?conversation_id=${conversationId}`
      );
      const conversationsData = await conversationsResponse.json();

      if (!conversationsResponse.ok) {
        throw new Error(`API error: ${conversationsResponse.status}`);
      }

      if (
        !conversationsData.conversations ||
        conversationsData.conversations.length === 0
      ) {
        throw new Error(
          `Conversation with ID ${conversationId} not found. Please check the conversations list for available conversations.`
        );
      }

      const leadId = conversationsData.conversations[0].lead_id;

      // Send the message
      const formData = new FormData();
      formData.append("lead_id", leadId.toString());
      formData.append("message", newMessage);

      const response = await fetch("http://localhost:8000/send-message", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to send message");
      }

      // Clear the input and refresh conversation
      setNewMessage("");
      fetchConversation();
    } catch (err) {
      console.error("Error sending message:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setSending(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case "new":
        return "bg-blue-100 text-blue-800";
      case "engaged":
        return "bg-green-100 text-green-800";
      case "booked":
        return "bg-purple-100 text-purple-800";
      case "opted_out":
        return "bg-red-100 text-red-800";
      case "unresponsive":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Conversation</h1>
          <Link href="/conversations" className="text-blue-600 hover:underline">
            Back to Conversations
          </Link>
        </div>
      </header>

      {loading ? (
        <div className="text-center py-8">Loading conversation...</div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
          <div className="mt-4">
            <Link
              href="/conversations"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Back to Conversations List
            </Link>
          </div>
        </div>
      ) : conversation ? (
        <div>
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-semibold">
                  {conversation.lead_name}
                </h2>
                <span
                  className={`px-2 py-1 rounded text-xs ${getStateColor(
                    conversation.state
                  )}`}
                >
                  {conversation.state}
                </span>
              </div>
              <div>
                <span className="text-gray-500">
                  {conversation.messages.length} messages
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Messages</h3>

            <div className="space-y-4 mb-6">
              {conversation.messages.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No messages yet.
                </p>
              ) : (
                conversation.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.is_from_lead ? "justify-start" : "justify-end"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.is_from_lead
                          ? "bg-gray-100 text-gray-800"
                          : "bg-blue-500 text-white"
                      }`}
                    >
                      <div className="text-sm">{message.content}</div>
                      <div
                        className={`text-xs mt-1 ${
                          message.is_from_lead
                            ? "text-gray-500"
                            : "text-blue-200"
                        }`}
                      >
                        {formatDate(message.sent_at)}
                        {!message.is_from_lead && (
                          <span className="ml-2">
                            {message.delivered
                              ? "✓ Delivered"
                              : "⚠️ Delivery issue"}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {conversation.state !== "opted_out" &&
              conversation.state !== "booked" && (
                <form onSubmit={handleSendMessage} className="mt-4">
                  <div className="flex">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type a message..."
                      className="flex-grow border border-gray-300 rounded-l p-2"
                      disabled={sending}
                    />
                    <button
                      type="submit"
                      className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700 disabled:bg-blue-300"
                      disabled={sending || !newMessage.trim()}
                    >
                      {sending ? "Sending..." : "Send"}
                    </button>
                  </div>
                </form>
              )}
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 p-8 rounded text-center">
          Conversation not found.
        </div>
      )}
    </div>
  );
}
