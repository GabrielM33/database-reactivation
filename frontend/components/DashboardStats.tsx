import React from "react";

interface StatsProps {
  stats: {
    totalLeads: number;
    activeConversations: number;
    booked: number;
    optedOut: number;
  };
}

const DashboardStats: React.FC<StatsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-white shadow rounded-lg p-6 border-l-4 border-blue-500">
        <div className="text-gray-500 font-medium text-sm">Total Leads</div>
        <div className="text-3xl font-bold mt-2">{stats.totalLeads}</div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 border-l-4 border-green-500">
        <div className="text-gray-500 font-medium text-sm">
          Active Conversations
        </div>
        <div className="text-3xl font-bold mt-2">
          {stats.activeConversations}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 border-l-4 border-purple-500">
        <div className="text-gray-500 font-medium text-sm">Booked Calls</div>
        <div className="text-3xl font-bold mt-2">{stats.booked}</div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 border-l-4 border-red-500">
        <div className="text-gray-500 font-medium text-sm">Opted Out</div>
        <div className="text-3xl font-bold mt-2">{stats.optedOut}</div>
      </div>
    </div>
  );
};

export default DashboardStats;
