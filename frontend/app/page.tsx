"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import DashboardStats from "../components/DashboardStats";
import LeadTable from "../components/LeadTable";
import ImportLeadsModal from "../components/ImportLeadsModal";
import { API_BASE_URL } from "@/utils/config";

interface Lead {
  id: number;
  name: string;
  phone_number: string;
  email: string | null;
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
}

export default function Home() {
  const [isImportModalOpen, setImportModalOpen] = useState(false);
  const [stats, setStats] = useState({
    totalLeads: 0,
    activeConversations: 0,
    booked: 0,
    optedOut: 0,
  });
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch leads
      const leadsResponse = await fetch(`${API_BASE_URL}/leads?limit=10`);
      const leadsData = await leadsResponse.json();

      if (!leadsResponse.ok) {
        throw new Error("Failed to fetch leads");
      }

      setLeads(leadsData.leads);

      // Calculate stats
      const statsData = {
        totalLeads: leadsData.total,
        activeConversations: 0,
        booked: 0,
        optedOut: 0,
      };

      // Fetch conversation counts by state
      const conversationsResponse = await fetch(
        `${API_BASE_URL}/conversations`
      );
      const conversationsData = await conversationsResponse.json();

      if (conversationsResponse.ok) {
        const conversations = conversationsData.conversations || [];
        statsData.activeConversations = conversations.filter(
          (c: Conversation) => c.state === "engaged" || c.state === "new"
        ).length;

        statsData.booked = conversations.filter(
          (c: Conversation) => c.state === "booked"
        ).length;
        statsData.optedOut = conversations.filter(
          (c: Conversation) => c.state === "opted_out"
        ).length;
      }

      setStats(statsData);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleImportSuccess = () => {
    fetchDashboardData();
    setImportModalOpen(false);
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">
          Database Reactivation Dashboard
        </h1>
        <p className="text-gray-600">
          Manage leads and monitor LLM-powered SMS conversations
        </p>
      </header>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <button
          onClick={() => setImportModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Import Leads
        </button>

        <Link
          href="/export-leads"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Export Leads
        </Link>

        <Link
          href="/conversations"
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
        >
          View Conversations
        </Link>
      </div>

      <DashboardStats stats={stats} />

      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Recent Leads</h2>
        {loading ? (
          <p>Loading leads data...</p>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        ) : (
          <>
            <LeadTable leads={leads} />
            {leads.length > 0 && (
              <div className="mt-4">
                <Link href="/leads" className="text-blue-600 hover:underline">
                  View all leads →
                </Link>
              </div>
            )}
          </>
        )}
      </div>

      {isImportModalOpen && (
        <ImportLeadsModal
          onClose={() => setImportModalOpen(false)}
          onSuccess={handleImportSuccess}
        />
      )}
    </div>
  );
}
