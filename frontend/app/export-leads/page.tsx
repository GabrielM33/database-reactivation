"use client";

import { useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/utils/config";

export default function ExportLeadsPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportUrl, setExportUrl] = useState<string | null>(null);

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    setExportUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/export-leads`, {
        method: "POST",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to export leads");
      }

      // In a real app, we would handle the file download here
      // For now, we'll just show a success message
      setExportUrl(data.file_path);
    } catch (err) {
      console.error("Error exporting leads:", err);
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <header className="mb-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Export Leads</h1>
          <Link href="/" className="text-blue-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
        <p className="text-gray-600 mt-2">
          Export all leads and their conversation data to a CSV file
        </p>
      </header>

      <div className="bg-white shadow rounded-lg p-6 max-w-md mx-auto">
        <p className="mb-6">
          Click the button below to export all leads and their conversation data
          to a CSV file. This process may take a few moments depending on the
          number of leads in the database.
        </p>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {exportUrl && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            Export completed successfully! The file is available on the server
            at: {exportUrl}
          </div>
        )}

        <button
          onClick={handleExport}
          disabled={loading}
          className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-green-300"
        >
          {loading ? "Exporting..." : "Export Leads to CSV"}
        </button>
      </div>
    </div>
  );
}
