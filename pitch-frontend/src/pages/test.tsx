import { useEffect } from 'react';
import Layout from '@/components/Layout';
import { useStore } from '@/lib/store';

export default function Test() {
  const { decks, loading, error, fetchDecks } = useStore();

  useEffect(() => {
    fetchDecks();
  }, [fetchDecks]);

  return (
    <Layout>
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Test Page</h1>
        
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Store State:</h2>
          <div className="bg-white p-4 rounded shadow">
            <p>Loading: {loading ? 'Yes' : 'No'}</p>
            <p>Error: {error || 'None'}</p>
            <p>Number of Decks: {decks.length}</p>
          </div>
        </div>

        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Deck List:</h2>
          {decks.length > 0 ? (
            <ul className="bg-white rounded shadow divide-y">
              {decks.map((deck) => (
                <li key={deck.id} className="p-4">
                  <p className="font-medium">{deck.name}</p>
                  <p className="text-sm text-gray-500">Status: {deck.status}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500">No decks found</p>
          )}
        </div>
      </div>
    </Layout>
  );
} 