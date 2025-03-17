"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface Lead {
  id: number;
  name: string;
  phone_number: string;
  email: string | null;
  additional_info?: string;
  created_at: string;
  updated_at: string;
  conversation_state?: string;
  last_contact?: string;
}

interface Conversation {
  id: number;
  lead_id: number;
  state: string;
  last_contact: string | null;
  booking_link_sent: boolean;
  booking_completed: boolean;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export default function LeadDetailPage() {
  const params = useParams();
  const leadId = params.id;

  const [lead, setLead] = useState<Lead | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeadData();
  }, [leadId]);

  const fetchLeadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch lead details
      const leadResponse = await fetch(
        `http://localhost:8000/leads?limit=1&lead_id=${leadId}`
      );
      const leadData = await leadResponse.json();

      if (!leadResponse.ok || !leadData.leads?.length) {
        throw new Error("Failed to fetch lead details");
      }

      setLead(leadData.leads[0]);

      // Fetch conversations for this lead
      const conversationsResponse = await fetch(
        `http://localhost:8000/conversations?lead_id=${leadId}`
      );
      const conversationsData = await conversationsResponse.json();

      if (conversationsResponse.ok) {
        setConversations(conversationsData.conversations || []);
      }
    } catch (err) {
      console.error("Error fetching lead data:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state?: string) => {
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

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Lead Details</h1>
          <Link href="/leads" className="text-blue-600 hover:underline">
            Back to Leads
          </Link>
        </div>
      </header>

      {loading ? (
        <div className="text-center py-8">Loading lead details...</div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      ) : lead ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Lead Information</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-500 text-sm">Name</p>
                  <p className="font-medium">{lead.name}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Phone Number</p>
                  <p className="font-medium">{lead.phone_number}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Email</p>
                  <p className="font-medium">{lead.email || "N/A"}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Status</p>
                  <p>
                    {lead.conversation_state ? (
                      <span
                        className={`px-2 py-1 rounded text-xs ${getStateColor(
                          lead.conversation_state
                        )}`}
                      >
                        {lead.conversation_state}
                      </span>
                    ) : (
                      "N/A"
                    )}
                  </p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Created</p>
                  <p className="font-medium">{formatDate(lead.created_at)}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Last Updated</p>
                  <p className="font-medium">{formatDate(lead.updated_at)}</p>
                </div>

                <div>
                  <p className="text-gray-500 text-sm">Last Contact</p>
                  <p className="font-medium">{formatDate(lead.last_contact)}</p>
                </div>
              </div>

              {lead.additional_info && (
                <div className="mt-4">
                  <p className="text-gray-500 text-sm">
                    Additional Information
                  </p>
                  <p className="font-medium whitespace-pre-wrap">
                    {lead.additional_info}
                  </p>
                </div>
              )}
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Conversations</h2>
                <Link
                  href={`/conversations?lead_id=${lead.id}`}
                  className="text-blue-600 hover:underline text-sm"
                >
                  View All
                </Link>
              </div>

              {conversations.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No conversations found for this lead.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-white">
                    <thead>
                      <tr className="bg-gray-100">
                        <th className="py-2 px-4 border-b text-left">Status</th>
                        <th className="py-2 px-4 border-b text-left">
                          Messages
                        </th>
                        <th className="py-2 px-4 border-b text-left">
                          Last Contact
                        </th>
                        <th className="py-2 px-4 border-b text-left">
                          Booking
                        </th>
                        <th className="py-2 px-4 border-b text-left">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {conversations.map((conversation) => (
                        <tr key={conversation.id} className="hover:bg-gray-50">
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
          </div>

          <div>
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Actions</h2>

              <div className="space-y-3">
                <Link
                  href={`/conversations/new?lead_id=${lead.id}`}
                  className="block w-full bg-blue-600 text-white text-center px-4 py-2 rounded hover:bg-blue-700"
                >
                  Start New Conversation
                </Link>

                <Link
                  href={`/leads/${lead.id}/edit`}
                  className="block w-full bg-gray-600 text-white text-center px-4 py-2 rounded hover:bg-gray-700"
                >
                  Edit Lead
                </Link>

                {conversations.length > 0 && (
                  <Link
                    href={`/conversations/${conversations[0].id}`}
                    className="block w-full bg-purple-600 text-white text-center px-4 py-2 rounded hover:bg-purple-700"
                  >
                    View Latest Conversation
                  </Link>
                )}
              </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Stats</h2>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-500">Total Conversations:</span>
                  <span className="font-medium">{conversations.length}</span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-500">Total Messages:</span>
                  <span className="font-medium">
                    {conversations.reduce(
                      (sum, conv) => sum + conv.message_count,
                      0
                    )}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-500">Booking Link Sent:</span>
                  <span className="font-medium">
                    {conversations.some((conv) => conv.booking_link_sent)
                      ? "Yes"
                      : "No"}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span className="text-gray-500">Booking Completed:</span>
                  <span className="font-medium">
                    {conversations.some((conv) => conv.booking_completed)
                      ? "Yes"
                      : "No"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 p-8 rounded text-center">
          Lead not found.
        </div>
      )}
    </div>
  );
}
