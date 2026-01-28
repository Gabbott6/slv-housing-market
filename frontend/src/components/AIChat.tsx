/**
 * AIChat component - AI-powered Q&A for housing codes and regulations.
 */
import React, { useState } from 'react';
import { aiApi } from '../services/api';
import type { AIAnswerResponse } from '../types/property';

const AIChat: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [jurisdiction, setJurisdiction] = useState('Salt Lake County');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AIAnswerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResponse(null);

      const result = await aiApi.askQuestion({
        question,
        jurisdiction: jurisdiction || undefined,
      });

      setResponse(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get answer. Please try again.');
      console.error('Error asking question:', err);
    } finally {
      setLoading(false);
    }
  };

  const exampleQuestions = [
    'What are the setback requirements for residential properties?',
    'What is the minimum ceiling height for bedrooms?',
    'Do I need a permit to build a deck?',
    'What are the parking requirements for new construction?',
  ];

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Housing Codes & Regulations Assistant
        </h2>
        <p className="text-gray-600 mb-6">
          Ask questions about building codes, zoning regulations, and housing laws in Salt Lake Valley.
        </p>

        {/* Question Form */}
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Example: What are the setback requirements for residential properties?"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jurisdiction (Optional)
            </label>
            <input
              type="text"
              value={jurisdiction}
              onChange={(e) => setJurisdiction(e.target.value)}
              placeholder="Salt Lake County"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-6 py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Getting Answer...' : 'Ask Question'}
          </button>
        </form>

        {/* Example Questions */}
        <div className="mb-6">
          <p className="text-sm font-medium text-gray-700 mb-2">Example Questions:</p>
          <div className="space-y-2">
            {exampleQuestions.map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className="block text-left text-sm text-primary-600 hover:text-primary-800 hover:underline"
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="border-t border-gray-200 pt-6">
            <div className="flex items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Answer:</h3>
              <span
                className={`ml-4 px-2 py-1 text-xs rounded ${
                  response.confidence === 'high'
                    ? 'bg-green-100 text-green-800'
                    : response.confidence === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {response.confidence} confidence
              </span>
            </div>

            <div className="prose max-w-none mb-6">
              <p className="text-gray-800 whitespace-pre-wrap">{response.answer}</p>
            </div>

            {/* Sources */}
            {response.sources && response.sources.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Sources:</h4>
                <div className="space-y-3">
                  {response.sources.map((source, index) => (
                    <div key={index} className="bg-gray-50 rounded-md p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-medium text-gray-900">
                            {source.code_section} - {source.title}
                          </p>
                          <p className="text-sm text-gray-600">{source.jurisdiction}</p>
                        </div>
                      </div>
                      {source.source_url && (
                        <a
                          href={source.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-primary-600 hover:underline"
                        >
                          View Source →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                <strong>Important:</strong> This information is provided as guidance only.
                Always consult with local building officials or a qualified professional for
                authoritative information.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIChat;
