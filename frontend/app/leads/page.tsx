"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import LeadTable from "../../components/LeadTable";

interface Lead {
  id: number;
  name: string;
  phone_number: string;
  email: string | null;
  conversation_state?: string;
  last_contact?: string;
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [totalLeads, setTotalLeads] = useState(0);
  const leadsPerPage = 20;

  useEffect(() => {
    fetchLeads();
  }, [filter, page]);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);

    try {
      let url = `http://localhost:8000/leads?skip=${
        (page - 1) * leadsPerPage
      }&limit=${leadsPerPage}`;
      if (filter !== "all") {
        url += `&state=${filter}`;
      }

      const response = await fetch(url);
      const data = await response.json();

      if (!response.ok) {
        throw new Error("Failed to fetch leads");
      }

      setLeads(data.leads);
      setTotalLeads(data.total);
    } catch (err) {
      console.error("Error fetching leads:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(totalLeads / leadsPerPage);

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Leads</h1>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
        <p className="text-gray-600 mt-2">
          View and manage all leads in the database
        </p>
      </header>

      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setFilter("all");
              setPage(1);
            }}
            className={`px-3 py-1 rounded-full ${
              filter === "all" ? "bg-gray-800 text-white" : "bg-gray-200"
            }`}
          >
            All
          </button>
          <button
            onClick={() => {
              setFilter("new");
              setPage(1);
            }}
            className={`px-3 py-1 rounded-full ${
              filter === "new" ? "bg-blue-600 text-white" : "bg-blue-100"
            }`}
          >
            New
          </button>
          <button
            onClick={() => {
              setFilter("engaged");
              setPage(1);
            }}
            className={`px-3 py-1 rounded-full ${
              filter === "engaged" ? "bg-green-600 text-white" : "bg-green-100"
            }`}
          >
            Engaged
          </button>
          <button
            onClick={() => {
              setFilter("booked");
              setPage(1);
            }}
            className={`px-3 py-1 rounded-full ${
              filter === "booked" ? "bg-purple-600 text-white" : "bg-purple-100"
            }`}
          >
            Booked
          </button>
          <button
            onClick={() => {
              setFilter("opted_out");
              setPage(1);
            }}
            className={`px-3 py-1 rounded-full ${
              filter === "opted_out" ? "bg-red-600 text-white" : "bg-red-100"
            }`}
          >
            Opted Out
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">Loading leads...</div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      ) : (
        <>
          <LeadTable leads={leads} />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-6">
              <nav className="flex items-center">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 rounded border mr-2 disabled:opacity-50"
                >
                  Previous
                </button>

                <div className="flex space-x-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    // Show pages around current page
                    let pageNum;
                    if (totalPages <= 5) {
                      pageNum = i + 1;
                    } else if (page <= 3) {
                      pageNum = i + 1;
                    } else if (page >= totalPages - 2) {
                      pageNum = totalPages - 4 + i;
                    } else {
                      pageNum = page - 2 + i;
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`w-8 h-8 rounded ${
                          page === pageNum
                            ? "bg-blue-600 text-white"
                            : "border hover:bg-gray-100"
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>

                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 rounded border ml-2 disabled:opacity-50"
                >
                  Next
                </button>
              </nav>
            </div>
          )}
        </>
      )}
    </div>
  );
}
