import React from "react";
import { useRouter } from "next/navigation";

interface Lead {
  id: number;
  name: string;
  phone_number: string;
  email: string | null;
  conversation_state?: string;
  last_contact?: string;
}

interface LeadTableProps {
  leads: Lead[];
}

const LeadTable: React.FC<LeadTableProps> = ({ leads }) => {
  const router = useRouter();

  if (leads.length === 0) {
    return (
      <div className="bg-gray-50 p-6 rounded text-center">
        No leads found. Import leads to get started.
      </div>
    );
  }

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

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A";

    const date = new Date(dateString);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString();
  };

  const handleViewDetails = (leadId: number) => {
    // Check if the lead exists in our current list
    const leadExists = leads.some((lead) => lead.id === leadId);
    if (leadExists) {
      router.push(`/leads/${leadId}`);
    } else {
      alert(
        `Lead with ID ${leadId} not found. Please refresh the page to see the latest leads.`
      );
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr className="bg-gray-100">
            <th className="py-2 px-4 border-b text-left">Name</th>
            <th className="py-2 px-4 border-b text-left">Phone</th>
            <th className="py-2 px-4 border-b text-left">Email</th>
            <th className="py-2 px-4 border-b text-left">Status</th>
            <th className="py-2 px-4 border-b text-left">Last Contact</th>
            <th className="py-2 px-4 border-b text-left">Action</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id} className="hover:bg-gray-50">
              <td className="py-2 px-4 border-b">{lead.name}</td>
              <td className="py-2 px-4 border-b">{lead.phone_number}</td>
              <td className="py-2 px-4 border-b">{lead.email || "N/A"}</td>
              <td className="py-2 px-4 border-b">
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
              </td>
              <td className="py-2 px-4 border-b">
                {formatDate(lead.last_contact)}
              </td>
              <td className="py-2 px-4 border-b">
                <button
                  onClick={() => handleViewDetails(lead.id)}
                  className="text-blue-600 hover:underline"
                >
                  View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LeadTable;
