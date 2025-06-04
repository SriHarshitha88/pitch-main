'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, X, FileText } from 'lucide-react';
import { useStore } from '@/lib/store';
import { useDropzone, FileRejection } from 'react-dropzone';

export default function NewDeckPage() {
  const router = useRouter();
  const { uploadDeck } = useStore();
  const [file, setFile] = useState<File | null>(null);
  const [startupName, setStartupName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    if (rejectedFiles.length > 0) {
      setError('Please upload a valid PDF or PPTX file');
      return;
    }
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !startupName) {
      setError('Please provide both a file and startup name');
      return;
    }

    try {
      setIsUploading(true);
      setError(null);
      await uploadDeck(file, startupName);
      router.push('/decks');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Upload New Deck</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="startupName" className="block text-sm font-medium text-gray-300">
            Startup Name
          </label>
          <input
            type="text"
            id="startupName"
            value={startupName}
            onChange={(e) => setStartupName(e.target.value)}
            className="mt-1 block w-full rounded-md bg-gray-700 border-gray-600 text-white shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            placeholder="Enter your startup name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Pitch Deck</label>
          <div
            {...getRootProps()}
            className={`mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-md ${
              isDragActive
                ? 'border-purple-500 bg-purple-500/10'
                : 'border-gray-600 hover:border-gray-500'
            }`}
          >
            <div className="space-y-1 text-center">
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-400">
                <p className="pl-1">Drag and drop your pitch deck, or click to select</p>
              </div>
              <p className="text-xs text-gray-500">PDF or PPTX up to 10MB</p>
            </div>
          </div>
        </div>

        {file && (
          <div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-300">{file.name}</span>
            </div>
            <button
              type="button"
              onClick={() => setFile(null)}
              className="text-gray-400 hover:text-gray-300"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-500/10 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-400">Error</h3>
                <div className="mt-2 text-sm text-red-300">{error}</div>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isUploading || !file || !startupName}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? 'Uploading...' : 'Upload Deck'}
          </button>
        </div>
      </form>
    </div>
  );
} 