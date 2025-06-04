'use client';

import { FileText, BarChart2, BookOpen, Upload } from 'lucide-react';
import Link from 'next/link';
import { useStore } from '@/lib/store';
import { useEffect } from 'react';
import { Deck } from '@/types';

const stats = [
  { name: 'Total Decks', value: '12', icon: FileText, color: 'text-blue-400' },
  { name: 'Analyses', value: '24', icon: BarChart2, color: 'text-purple-400' },
  { name: 'Knowledge Files', value: '8', icon: BookOpen, color: 'text-green-400' },
];

export default function DashboardPage() {
  const { decks, fetchDecks } = useStore();

  useEffect(() => {
    fetchDecks();
  }, [fetchDecks]);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link
          href="/decks/new"
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
        >
          <Upload className="h-5 w-5 mr-2" />
          Upload New Deck
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="relative overflow-hidden rounded-lg bg-gray-800 px-4 py-5 shadow sm:px-6 sm:py-6"
          >
            <dt>
              <div className={`absolute rounded-md bg-gray-700 p-3 ${stat.color}`}>
                <stat.icon className="h-6 w-6" aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-gray-300">{stat.name}</p>
            </dt>
            <dd className="ml-16 flex items-baseline">
              <p className="text-2xl font-semibold text-white">{stat.value}</p>
            </dd>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="rounded-lg bg-gray-800 shadow">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg font-medium leading-6 text-white">Recent Activity</h3>
        </div>
        <div className="border-t border-gray-700">
          <ul role="list" className="divide-y divide-gray-700">
            {decks.slice(0, 5).map((deck: Deck) => (
              <li key={deck.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <FileText className="h-6 w-6 text-gray-400" />
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-white">{deck.startup_name}</p>
                      <p className="text-sm text-gray-300">
                        Analyzed {new Date(deck.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="ml-2 flex-shrink-0">
                    <Link
                      href={`/decks/${deck.id}`}
                      className="inline-flex items-center rounded-md bg-gray-700 px-2.5 py-1.5 text-sm font-medium text-white hover:bg-gray-600"
                    >
                      View
                    </Link>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          href="/decks/new"
          className="relative block rounded-lg border-2 border-dashed border-gray-700 p-12 text-center hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
        >
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <span className="mt-2 block text-sm font-medium text-gray-300">Upload New Deck</span>
        </Link>
        <Link
          href="/knowledge"
          className="relative block rounded-lg border-2 border-dashed border-gray-700 p-12 text-center hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
        >
          <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
          <span className="mt-2 block text-sm font-medium text-gray-300">Manage Knowledge Base</span>
        </Link>
        <Link
          href="/analytics"
          className="relative block rounded-lg border-2 border-dashed border-gray-700 p-12 text-center hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
        >
          <BarChart2 className="mx-auto h-12 w-12 text-gray-400" />
          <span className="mt-2 block text-sm font-medium text-gray-300">View Analytics</span>
        </Link>
      </div>
    </div>
  );
} 