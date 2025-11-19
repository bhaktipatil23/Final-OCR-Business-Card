import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from "@/components/layout/Navbar";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface ExtractedData {
  name: string;
  phone: string;
  email: string;
  company: string;
  designation: string;
  address: string;
}

const EmailPage = () => {
  const location = useLocation();
  const { eventData, extractedData } = location.state || {};
  
  const [selectedEvent, setSelectedEvent] = useState(eventData?.event || '');
  const [emailData, setEmailData] = useState({
    to: '',
    subject: 'Partnership Opportunity with ReCircle - Sustainable Business Solutions',
    body: `Hello [Recipient Name],\n\nI hope this email finds you well. I am writing to introduce you to ReCircle, an innovative company focused on sustainable business solutions and circular economy practices.\n\nReCircle specializes in:\n• Sustainable waste management solutions\n• Circular economy consulting\n• Environmental impact reduction strategies\n• Green technology implementation\n\nWe believe there could be excellent synergy between our organizations and would love to explore potential partnership opportunities.\n\nWould you be available for a brief call next week to discuss how we might collaborate?\n\nBest regards,\n[Sender Name]\nReCircle Team`
  });
  
  const [attachmentFile, setAttachmentFile] = useState<File | null>(null);
  const [attachmentPath, setAttachmentPath] = useState<string>('');
  const [signatureFile, setSignatureFile] = useState<File | null>(null);
  const [signaturePath, setSignaturePath] = useState<string>('');


  const [filterType, setFilterType] = useState('send-all');
  const [selectedPeople, setSelectedPeople] = useState<string[]>([]);
  const [allNames, setAllNames] = useState<string[]>([]);
  const [selectedName, setSelectedName] = useState<string>('');
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('');
  const [allContacts, setAllContacts] = useState<ExtractedData[]>([]);
  const [filteredContacts, setFilteredContacts] = useState<ExtractedData[]>([]);
  const [showPeopleModal, setShowPeopleModal] = useState(false);

  
  // Fetch all names on component mount
  useEffect(() => {
    fetchAllNames();
    fetchAllContacts();
  }, []);

  const fetchAllNames = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/names');
      const data = await response.json();
      setAllNames(data.names || []);
    } catch (error) {
      console.error('Error fetching names:', error);
      toast.error('Failed to fetch names');
    }
  };

  const fetchAllContacts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/contacts');
      const data = await response.json();
      setAllContacts(data.contacts || []);
      setFilteredContacts(data.contacts || []);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      toast.error('Failed to fetch contacts');
    }
  };

  const fetchEventsByName = async (name: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/events/${encodeURIComponent(name)}`);
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Failed to fetch events');
    }
  };

  const fetchContactsByBatch = async (batchId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/contacts/by-batch/${encodeURIComponent(batchId)}`);
      const data = await response.json();
      setFilteredContacts(data.contacts || []);
    } catch (error) {
      console.error('Error fetching contacts by batch:', error);
      toast.error('Failed to fetch contacts by batch');
    }
  };

  // Handle name selection
  const handleNameChange = (name: string) => {
    setSelectedName(name);
    setSelectedEventId('');
    setEvents([]);
    if (name) {
      fetchEventsByName(name);
      setFilteredContacts(allContacts); // Show all contacts when name is selected
    } else {
      setFilteredContacts(allContacts);
    }
  };

  // Handle event selection
  const handleEventChange = (eventId: string) => {
    setSelectedEventId(eventId);
    if (eventId) {
      const selectedEvent = events.find(e => e.batch_id === eventId);
      if (selectedEvent) {
        fetchContactsByBatch(selectedEvent.batch_id);
      }
    } else {
      setFilteredContacts(allContacts);
    }
  };

  const people: ExtractedData[] = filteredContacts;
  

  
  const handleFilterTypeChange = (type: string) => {
    setFilterType(type);
    if (type === 'send-all') {
      const individualEmails = people.map(p => {
        if (p.email && p.email.includes('@')) {
          return p.email.split(',')[0].trim();
        }
        return null;
      }).filter(Boolean);
      setSelectedPeople(individualEmails);
    } else if (type === 'particular' || type === 'exclude') {
      setShowPeopleModal(true);
    }
  };
  
  useEffect(() => {
    if (filterType === 'send-all') {
      const individualEmails = people.map(p => {
        if (p.email && p.email.includes('@')) {
          return p.email.split(',')[0].trim();
        }
        return null;
      }).filter(Boolean);
      setSelectedPeople(individualEmails);
    }
  }, [people]);

  // Auto-populate TO field when contacts are filtered
  useEffect(() => {
    const emails = people.map(p => p.email).filter(Boolean).join(', ');
    setEmailData(prev => ({ ...prev, to: emails }));
  }, [people]);


  
  const handlePersonToggle = (email: string) => {
    setSelectedPeople(prev => 
      prev.includes(email) 
        ? prev.filter(e => e !== email)
        : [...prev, email]
    );
  };
  
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachmentFile(file);
    }
  };
  
  const handleSignatureSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSignatureFile(file);
    }
  };
  
  const handleSendEmail = async () => {
    if (selectedPeople.length === 0) {
      toast.error('Please select at least one recipient');
      return;
    }
    
    if (!selectedName) {
      toast.error('Please select a name first');
      return;
    }
    
    try {
      let uploadedAttachmentPath = '';
      let uploadedSignaturePath = '';
      
      // Upload attachment if selected
      if (attachmentFile) {
        const formData = new FormData();
        formData.append('file', attachmentFile);
        
        const uploadResponse = await fetch('http://localhost:8000/api/v1/upload-attachment', {
          method: 'POST',
          body: formData
        });
        
        if (uploadResponse.ok) {
          const uploadResult = await uploadResponse.json();
          uploadedAttachmentPath = uploadResult.file_path;
          toast.success('Attachment uploaded successfully');
        } else {
          toast.error('Failed to upload attachment');
          return;
        }
      }
      
      // Upload signature if selected
      if (signatureFile) {
        const formData = new FormData();
        formData.append('file', signatureFile);
        
        const uploadResponse = await fetch('http://localhost:8000/api/v1/upload-attachment', {
          method: 'POST',
          body: formData
        });
        
        if (uploadResponse.ok) {
          const uploadResult = await uploadResponse.json();
          uploadedSignaturePath = uploadResult.file_path;
          toast.success('Signature uploaded successfully');
        } else {
          toast.error('Failed to upload signature');
          return;
        }
      }
      
      // Prepare unique recipients (first occurrence only)
      const uniqueRecipients = [];
      const seenEmails = new Set();
      
      for (const email of selectedPeople) {
        if (!seenEmails.has(email) && email.includes('@')) {
          // Find contact by checking if the email matches the first email in their email field
          const contact = people.find(p => p.email && p.email.split(',')[0].trim() === email);
          uniqueRecipients.push({
            email: email.trim(),
            name: contact?.name || 'Business Partner'
          });
          seenEmails.add(email);
        }
      }
      
      // Send to API with template body - personalization will be handled by backend
      const response = await fetch('http://localhost:8000/api/v1/send-emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipients: uniqueRecipients,
          subject: emailData.subject,
          body: emailData.body.replace('[Sender Name]', selectedName || 'Team Member'),
          attachment_path: uploadedAttachmentPath || null,
          signature_path: uploadedSignaturePath || null
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        toast.success(`${result.count} emails added to queue and processing started!`);
        // Show queue status
        setTimeout(() => checkQueueStatus(), 2000);
      } else {
        toast.error(`Error: ${result.detail}`);
      }
      
    } catch (error) {
      console.error('Error sending emails:', error);
      toast.error('Failed to send emails');
    }
  };
  
  const checkQueueStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/queue-status');
      const status = await response.json();
      
      if (status.processing) {
        toast.info(`Processing emails... Sent: ${status.sent}, Remaining: ${status.queued}`);
        setTimeout(() => checkQueueStatus(), 3000);
      } else {
        toast.success(`Email processing completed! Sent: ${status.sent}, Failed: ${status.failed}`);
      }
    } catch (error) {
      console.error('Error checking queue status:', error);
    }
  };
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 w-full mx-auto px-2 sm:px-4 lg:px-8 py-2 sm:py-4">
        <div className="max-w-4xl mx-auto space-y-3 sm:space-y-6">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 px-2 sm:px-0">Send Email</h1>
          
          {/* Name and Event Filters */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0 space-y-4">
            <h3 className="text-base sm:text-lg font-medium text-gray-900">Filter Options</h3>
            
            {/* Name Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
              <select 
                value={selectedName}
                onChange={(e) => handleNameChange(e.target.value)}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Name</option>
                {allNames.map(name => (
                  <option key={name} value={name}>{name}</option>
                ))}
              </select>
            </div>
            
            {/* Event Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Event</label>
              <select 
                value={selectedEventId}
                onChange={(e) => handleEventChange(e.target.value)}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!selectedName}
              >
                <option value="">
                  {selectedName ? 'Select Event' : 'Select a name first'}
                </option>
                {events.map(event => (
                  <option key={event.batch_id} value={event.batch_id}>
                    {event.event_name} ({event.team})
                  </option>
                ))}
              </select>
            </div>
            
            <div className="text-sm text-gray-600">
              Showing {people.length} contacts
            </div>
          </div>
          
          {/* Email Form */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0 space-y-3 sm:space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">TO</label>
              <input 
                type="text"
                value={emailData.to}
                onChange={(e) => setEmailData({...emailData, to: e.target.value})}
                placeholder="Recipients will be auto-filled based on selection below"
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                readOnly
              />
            </div>
            

            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SUBJECT</label>
              <input 
                type="text"
                value={emailData.subject}
                onChange={(e) => setEmailData({...emailData, subject: e.target.value})}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">BODY</label>
              <textarea 
                value={emailData.body}
                onChange={(e) => setEmailData({...emailData, body: e.target.value})}
                rows={8}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 sm:rows-12"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">SIGNATURE (Optional)</label>
              <p className="text-xs text-gray-500 mb-2">Company signature image (JPG, PNG)</p>
              <input 
                type="file"
                accept=".jpg,.jpeg,.png"
                onChange={handleSignatureSelect}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {signatureFile && (
                <div className="mt-2">
                  <p className="text-sm text-green-600 mb-1">Selected: {signatureFile.name}</p>
                  <img 
                    src={URL.createObjectURL(signatureFile)} 
                    alt="Signature preview" 
                    className="max-w-xs max-h-20 border rounded"
                  />
                </div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ATTACHMENT (Optional)</label>
              <p className="text-xs text-gray-500 mb-2">Supported: PDF, DOC, JPG, PNG</p>
              <input 
                type="file"
                accept=".pdf,.doc,.jpg,.jpeg,.png"
                onChange={handleFileSelect}
                className="w-full px-3 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {attachmentFile && (
                <p className="text-sm text-green-600 mt-1">Selected: {attachmentFile.name}</p>
              )}
            </div>
          </div>
          
          {/* Filter Options */}
          <div className="bg-white p-3 sm:p-4 rounded-lg border mx-2 sm:mx-0">
            <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">Send Options</h3>
            <div className="space-y-2 sm:space-y-3">
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="send-all"
                  checked={filterType === 'send-all'}
                  onChange={(e) => handleFilterTypeChange(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span className="break-words">Send to All ({people.length} people)</span>
              </label>
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="particular"
                  checked={filterType === 'particular'}
                  onChange={(e) => handleFilterTypeChange(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span>Send to Particular Person</span>
              </label>
              <label className="flex items-center text-sm sm:text-base">
                <input 
                  type="radio" 
                  name="filter" 
                  value="exclude"
                  checked={filterType === 'exclude'}
                  onChange={(e) => handleFilterTypeChange(e.target.value)}
                  className="mr-2 sm:mr-3"
                />
                <span>Exclude Person</span>
              </label>
            </div>
          </div>
          

          
          {/* Send Button */}
          <div className="flex justify-center px-2 sm:px-0 pb-4 sm:pb-0">
            <button 
              onClick={handleSendEmail}
              className="w-full sm:w-auto px-4 sm:px-8 py-3 text-sm sm:text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium max-w-sm"
            >
              Send Email to {selectedPeople.length} recipient(s)
            </button>
          </div>
        </div>
      </main>
      

      
      {/* People Selection Modal */}
      {showPeopleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <h2 className="text-lg font-bold mb-4">
              {filterType === 'particular' ? 'Select People to Send' : 'Select People to Exclude'}
            </h2>
            <div className="space-y-2 mb-4">
              {people.map((person, index) => {
                const email = person.email?.split(',')[0].trim();
                if (!email) return null;
                return (
                  <label key={index} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedPeople.includes(email)}
                      onChange={() => handlePersonToggle(email)}
                      className="mr-2"
                    />
                    <span className="text-sm">{person.name} ({email})</span>
                  </label>
                );
              })}
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setShowPeopleModal(false);
                  setFilterType('send-all');
                  setSelectedPeople([]);
                }}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (filterType === 'exclude') {
                    const allEmails = people.map(p => p.email?.split(',')[0].trim()).filter(Boolean);
                    const excludedEmails = allEmails.filter(email => !selectedPeople.includes(email));
                    setSelectedPeople(excludedEmails);
                  }
                  setShowPeopleModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailPage;