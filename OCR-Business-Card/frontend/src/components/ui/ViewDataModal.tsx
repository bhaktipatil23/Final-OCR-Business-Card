import { useState, useEffect } from "react";
import { X, Search, ArrowLeft } from "lucide-react";
import { apiService } from "@/services/api";

interface ViewDataModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface SavedBatch {
  batch_id: string;
  name: string;
  team: string;
  event: string;
  created_at: string;
  total_records: number;
}

interface BusinessCardRecord {
  card_name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
  image_data: string;
  form_name: string;
  event: string;
  team: string;
  remark: string;
}

const ViewDataModal = ({ isOpen, onClose }: ViewDataModalProps) => {
  const [batches, setBatches] = useState<SavedBatch[]>([]);
  const [filteredBatches, setFilteredBatches] = useState<SavedBatch[]>([]);
  const [searchRecords, setSearchRecords] = useState<BusinessCardRecord[]>([]);
  const [filterType, setFilterType] = useState<'name' | 'name_team' | 'name_event'>('name');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'batches' | 'search'>('batches');
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSavedBatches();
    }
  }, [isOpen]);

  useEffect(() => {
    filterBatches();
  }, [batches, filterType, searchTerm]);

  const fetchSavedBatches = async () => {
    try {
      setLoading(true);
      const hostname = window.location.hostname;
      const baseUrl = hostname === 'localhost' || hostname === '127.0.0.1' 
        ? 'http://localhost:8000' 
        : `http://${hostname}:8000`;
      
      const response = await fetch(`${baseUrl}/api/v1/saved-batches`);
      const data = await response.json();
      setBatches(data.batches || []);
    } catch (error) {
      console.error('Error fetching saved batches:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterBatches = () => {
    if (!searchTerm) {
      setFilteredBatches(batches);
      return;
    }

    const filtered = batches.filter(batch => {
      const value = batch[filterType];
      return value && value.toLowerCase().includes(searchTerm.toLowerCase());
    });
    setFilteredBatches(filtered);
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setViewMode('batches');
      return;
    }

    try {
      setSearchLoading(true);
      const data = await apiService.searchRecords(filterType, searchTerm);
      setSearchRecords(data.records || []);
      setViewMode('search');
    } catch (error) {
      console.error('Error searching records:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const resetToList = () => {
    setViewMode('batches');
    setSearchTerm('');
    setSearchRecords([]);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-hidden">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            {viewMode === 'batches' ? 'View Saved Data' : `Search Results - ${filterType}`}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="flex gap-4 mb-4">
          {viewMode === 'search' && (
            <button
              onClick={resetToList}
              className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft size={20} />
              Back to List
            </button>
          )}
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as 'name' | 'name_team' | 'name_event')}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="name">Search by Name</option>
            <option value="name_team">Search by Name & Team</option>
            <option value="name_event">Search by Name & Event</option>
          </select>
          
          {filterType === 'name' ? (
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search by form name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md"
              />
            </div>
          ) : (
            <div className="flex gap-2 flex-1">
              <input
                type="text"
                placeholder="Name"
                value={searchTerm.split(',')[0] || ''}
                onChange={(e) => {
                  const parts = searchTerm.split(',');
                  setSearchTerm(`${e.target.value},${parts[1] || ''}`);
                }}
                onKeyPress={handleKeyPress}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
              />
              <input
                type="text"
                placeholder={filterType === 'name_team' ? 'Team' : 'Event'}
                value={searchTerm.split(',')[1] || ''}
                onChange={(e) => {
                  const parts = searchTerm.split(',');
                  setSearchTerm(`${parts[0] || ''},${e.target.value}`);
                }}
                onKeyPress={handleKeyPress}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          )}
          
          <button
            onClick={handleSearch}
            disabled={searchLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {searchLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="overflow-y-auto max-h-96">
          {viewMode === 'batches' ? (
            // Show batches/events list
            loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : filteredBatches.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No data found</div>
            ) : (
              <div className="space-y-2">
                {filteredBatches.map((batch, index) => (
                  <div key={`batch-${index}-${batch.name || 'unknown'}`} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                    <div className="space-y-3">
                      <div>
                        <span className="font-medium text-gray-700">Records:</span>
                        <p className="text-gray-900">{batch.total_records}</p>
                      </div>
                      <div className="text-sm text-gray-500">
                        Created: {new Date(batch.created_at).toLocaleString()}
                      </div>
                      <div className="flex gap-6 pt-2 border-t border-gray-100">
                        <div>
                          <span className="font-medium text-gray-700">Name:</span>
                          <span className="ml-2 text-gray-900">{batch.name}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Team:</span>
                          <span className="ml-2 text-gray-900">{batch.team}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Event:</span>
                          <span className="ml-2 text-gray-900">{batch.event}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            // Show search results
            searchLoading ? (
              <div className="text-center py-8">Searching...</div>
            ) : searchRecords.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No records found for "{searchTerm}"
              </div>
            ) : (
              <div>
                <div className="text-sm text-gray-600 mb-3">
                  Found {searchRecords.length} record(s) for "{searchTerm}"
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Sr No</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Image</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Card Name</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Phone</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Email</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Company</th>

                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Designation</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Form Name</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Team</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Event</th>
                        <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase border-b">Remark</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white">
                      {searchRecords.map((record, index) => (
                        <tr key={`record-${index}-${record.card_name || 'unknown'}-${record.phone || 'no-phone'}`} className="hover:bg-gray-50">
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{index + 1}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">
                            {record.image_data ? (
                              <img 
                                src={`data:image/jpeg;base64,${record.image_data}`} 
                                alt="Business Card" 
                                className="w-20 h-12 object-contain rounded border cursor-pointer hover:scale-110 transition-transform shadow-sm"
                                onClick={() => {
                                  const modal = document.createElement('div');
                                  modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50';
                                  modal.innerHTML = `
                                    <div class="relative bg-white rounded-lg p-4 max-w-lg max-h-[90vh] overflow-auto">
                                      <div class="flex justify-between items-center mb-4">
                                        <h3 class="text-lg font-semibold">Business Card</h3>
                                        <button class="text-gray-500 hover:text-gray-700" onclick="this.parentElement.parentElement.parentElement.remove()">
                                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                                          </svg>
                                        </button>
                                      </div>
                                      <img src="data:image/jpeg;base64,${record.image_data}" class="w-full h-auto rounded border shadow-sm" />
                                    </div>
                                  `;
                                  modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
                                  document.body.appendChild(modal);
                                }}
                              />
                            ) : (
                              <span className="text-gray-400 text-xs">No Image</span>
                            )}
                          </td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.card_name}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.phone}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.email}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.company}</td>

                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.designation}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.form_name || 'N/A'}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.team}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">{record.event}</td>
                          <td className="px-3 py-2 text-sm text-gray-900 border-b">
                            <input 
                              type="text" 
                              value={record.remark || ''} 
                              placeholder="Add remark..."
                              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                              readOnly
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default ViewDataModal;