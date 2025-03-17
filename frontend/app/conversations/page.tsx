"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/utils/config";

interface Conversation {
  id: number;
  lead_id: number;
  lead_name: string;
  state: string;
  last_contact: string | null;
  booking_link_sent: boolean;
  booking_completed: boolean;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export default function ConversationsPage() {
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [stateFilter, setStateFilter] = useState<string>("all");
  const pageSize = 100; // Just use a fixed page size

  useEffect(() => {
    fetchConversations();
  }, [stateFilter]);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);

    try {
      let url = `${API_BASE_URL}/conversations`;

      // Add query parameters
      const params = new URLSearchParams();
      params.append("limit", pageSize.toString());
      if (stateFilter && stateFilter !== "all") {
        params.append("state", stateFilter);
      }
      url += `?${params.toString()}`;

      const response = await fetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error("Failed to fetch conversations");
      }

      setConversations(data.conversations || []);
    } catch (err) {
      console.error("Error fetching conversations:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
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

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Conversations</h1>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
        <p className="text-gray-600 mt-2">
          View and manage conversations with leads
        </p>
      </header>

      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setStateFilter("all")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "all" ? "bg-gray-800 text-white" : "bg-gray-200"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setStateFilter("new")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "new" ? "bg-blue-600 text-white" : "bg-blue-100"
            }`}
          >
            New
          </button>
          <button
            onClick={() => setStateFilter("engaged")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "engaged"
                ? "bg-green-600 text-white"
                : "bg-green-100"
            }`}
          >
            Engaged
          </button>
          <button
            onClick={() => setStateFilter("booked")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "booked"
                ? "bg-purple-600 text-white"
                : "bg-purple-100"
            }`}
          >
            Booked
          </button>
          <button
            onClick={() => setStateFilter("opted_out")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "opted_out"
                ? "bg-red-600 text-white"
                : "bg-red-100"
            }`}
          >
            Opted Out
          </button>
          <button
            onClick={() => setStateFilter("unresponsive")}
            className={`px-3 py-1 rounded-full ${
              stateFilter === "unresponsive"
                ? "bg-yellow-600 text-white"
                : "bg-yellow-100"
            }`}
          >
            Unresponsive
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading conversations...</div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      ) : conversations.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded text-center">
          No conversations found with the selected filter.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 border-b text-left">Lead</th>
                <th className="py-2 px-4 border-b text-left">Status</th>
                <th className="py-2 px-4 border-b text-left">Messages</th>
                <th className="py-2 px-4 border-b text-left">Last Contact</th>
                <th className="py-2 px-4 border-b text-left">Booking</th>
                <th className="py-2 px-4 border-b text-left">Action</th>
              </tr>
            </thead>
            <tbody>
              {conversations.map((conversation) => (
                <tr key={conversation.id} className="hover:bg-gray-50">
                  <td className="py-2 px-4 border-b">
                    {conversation.lead_name}
                  </td>
                  <td className="py-2 px-4 border-b">
                    <span
                      className={`px-2 py-1 rounded text-xs ${getStateColor(
                        conversation.state
                      )}`}
                    >
                      {conversation.state}
                    </span>
                  </td>
                  <td className="py-2 px-4 border-b">
                    {conversation.message_count}
                  </td>
                  <td className="py-2 px-4 border-b">
                    {formatDate(conversation.last_contact)}
                  </td>
                  <td className="py-2 px-4 border-b">
                    {conversation.booking_completed ? (
                      <span className="text-green-600">Completed</span>
                    ) : conversation.booking_link_sent ? (
                      <span className="text-blue-600">Link Sent</span>
                    ) : (
                      <span className="text-gray-500">Not Sent</span>
                    )}
                  </td>
                  <td className="py-2 px-4 border-b">
                    <Link
                      href={`/conversations/${conversation.id}`}
                      className="text-blue-600 hover:underline"
                    >
                      View Messages
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
