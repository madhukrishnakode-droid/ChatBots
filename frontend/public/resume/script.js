/* ==================== Constants & Configuration ==================== */

const API_BASE_URL = 'http://localhost:8000';
const DEBOUNCE_DELAY = 300;

let resumeData = {
    skills: ["git", "github", "python", "java", "leadership"],
    experience_years: 0,
    projects: []
};
let currentJobs = [];
let userContext = {
    skills: ["git", "github", "python", "java", "leadership"],
    experience_years: 0
};

/* ==================== DOM Elements ==================== */

const resumeFile = document.getElementById('resume-file');
const uploadBtn = document.getElementById('upload-btn');
const resumeInfo = document.getElementById('resume-info');
const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const searchJobsBtn = document.getElementById('search-jobs-btn');
const jobsContainer = document.getElementById('jobs-container');
const modal = document.getElementById('job-modal');
const modalBody = document.getElementById('modal-body');
const closeBtn = document.querySelector('.close');
const loadingSpinner = document.getElementById('loading-spinner');

/* ==================== Event Listeners ==================== */

// Add error handling for null elements
if (!uploadBtn) {
    console.error('Upload button not found');
} else {
    uploadBtn.addEventListener('click', () => {
        if (resumeFile) resumeFile.click();
    });
}

if (resumeFile) {
    resumeFile.addEventListener('change', handleResumeUpload);
} else {
    console.error('Resume file input not found');
}

if (sendBtn) {
    sendBtn.addEventListener('click', sendChatMessage);
} else {
    console.error('Send button not found');
}

if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            sendChatMessage();
        }
    });
} else {
    console.error('Chat input not found');
}

if (searchJobsBtn) {
    searchJobsBtn.addEventListener('click', searchJobs);
} else {
    console.error('Search jobs button not found');
}

if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
} else {
    console.error('Close button not found');
}

if (modal) {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
} else {
    console.error('Modal not found');
}

/* ==================== Resume Upload & Parsing ==================== */

async function handleResumeUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/upload-resume`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Upload failed');
        }

        resumeData = data.resume_data;
        userContext = {
            skills: resumeData.skills,
            experience_years: resumeData.experience_years
        };

        displayResumeInfo(resumeData);
        addBotMessage(data.initial_greeting);
        enableChatAndSearch();
        
        // Clear file input
        resumeFile.value = '';

    } catch (error) {
        console.error('Error uploading resume:', error);
        addBotMessage(`❌ Error: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayResumeInfo(data) {
    resumeInfo.innerHTML = `
        <div class="resume-stat">
            <div class="resume-stat-label">Total Skills</div>
            <div class="resume-stat-value">${data.skills.length}</div>
        </div>
        
        <div class="resume-stat">
            <div class="resume-stat-label">Experience</div>
            <div class="resume-stat-value">${data.experience_years || '0'} yrs</div>
        </div>
        
        <div class="resume-stat">
            <div class="resume-stat-label">Projects</div>
            <div class="resume-stat-value">${data.projects.length}</div>
        </div>
        
        <div class="resume-skills">
            <h4>🛠️ Top Skills</h4>
            ${data.skills.slice(0, 8).map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
            ${data.skills.length > 8 ? `<span class="skill-tag">+${data.skills.length - 8} more</span>` : ''}
        </div>
    `;
}

/* ==================== Job Search & Matching ==================== */

async function searchJobs() {
    if (!resumeData) {
        addBotMessage('Please upload your resume first!');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/search-jobs`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    skills: resumeData.skills,
                    experience_years: resumeData.experience_years,
                    location: 'Remote'
                })
            }
        );

        if (!response.ok) throw new Error('Job search failed');

        const data = await response.json();
        currentJobs = data.jobs || data;

        displayJobs(currentJobs);
        addBotMessage(`Found ${currentJobs.length} matching job opportunities! Click on any job card to see details.`);

    } catch (error) {
        console.error('Error searching jobs:', error);
        addBotMessage('❌ Error searching jobs. Please try again.');
    } finally {
        showLoading(false);
    }
}

function displayJobs(jobs) {
    if (!jobs || jobs.length === 0) {
        jobsContainer.innerHTML = '<p class="placeholder">No matching jobs found</p>';
        return;
    }

    jobsContainer.innerHTML = jobs.map((job, index) => `
        <div class="job-card ${getMatchStrength(job.match_percentage || 0)}" 
             onclick="showJobDetails(${index})"
             style="cursor: pointer;">
            <div class="job-card-title">${truncate(job.title, 25)}</div>
            <div class="job-card-company">${truncate(job.company, 20)}</div>
            <div class="job-card-match">
                <span class="match-percentage">${job.match_percentage || 0}%</span>
                <div class="match-bar">
                    <div class="match-fill" style="width: ${job.match_percentage || 0}%"></div>
                </div>
            </div>
        </div>
    `).join('');
}

function showJobDetails(index) {
    const job = currentJobs[index];
    
    const matchPercentage = job.match_percentage || 0;
    const matchedSkills = job.matched_skills || [];
    const missingSkills = job.missing_skills || [];
    
    modalBody.innerHTML = `
        <h2>${job.title}</h2>
        <p><strong>${job.company}</strong> • ${job.location || 'Remote'}</p>
        
        <h3>📊 Match Score: ${matchPercentage}%</h3>
        <div class="match-bar" style="margin: 10px 0; height: 8px;">
            <div class="match-fill" style="width: ${matchPercentage}%"></div>
        </div>
        <p><strong>Strength:</strong> ${getMatchStrength(matchPercentage)}</p>
        
        <h3>✅ Your Matching Skills</h3>
        <div class="skill-list">
            ${matchedSkills.length > 0 ? matchedSkills.map(skill => `<span class="tag">${skill}</span>`).join('') : '<p>No matching skills identified</p>'}
        </div>
        
        <h3>❌ Skills to Develop</h3>
        <div class="skill-list">
            ${missingSkills.length > 0 ? missingSkills.map(skill => `<span class="tag">${skill}</span>`).join('') : '<p>You have all required skills!</p>'}
        </div>
        
        <h3>💰 Salary Range</h3>
        <p>${job.salary || 'Not specified'}</p>
        
        <h3>📝 Description</h3>
        <p>${job.description || 'No description available'}</p>
    `;
    
    modal.classList.add('show');

    // Add job info to chat context
    addBotMessage(`I found a great match! The <strong>${job.title}</strong> role at <strong>${job.company}</strong> has a <strong>${matchPercentage}%</strong> match. You have ${matchedSkills.length} of the required skills. Ask me anything about this role!`);
}

function closeModal() {
    modal.classList.remove('show');
}

/* ==================== Chat Functionality ==================== */

async function sendChatMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addUserMessage(message);
    chatInput.value = '';
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                context: userContext,
                user_id: 1
            })
        });

        if (!response.ok) throw new Error('Chat request failed');

        const data = await response.json();
        addBotMessage(data.bot_reply || data.response || 'I understood your message.');

    } catch (error) {
        console.error('Error sending message:', error);
        addBotMessage('❌ I had trouble processing that. Try again!');
    } finally {
        showLoading(false);
    }
}

function addUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="message-content">${escapeHtml(message)}</div>
        <div class="message-time">${getTimeString()}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollChatToBottom();
}

function addBotMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.innerHTML = `
        <div class="message-content">${message}</div>
        <div class="message-time">${getTimeString()}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollChatToBottom();
}

function scrollChatToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/* ==================== UI Helper Functions ==================== */

function enableChatAndSearch() {
    chatInput.disabled = false;
    sendBtn.disabled = false;
    searchJobsBtn.disabled = false;
}

function showLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('hidden');
    } else {
        loadingSpinner.classList.add('hidden');
    }
}

function getTimeString() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function truncate(str, length) {
    return str.length > length ? str.substring(0, length) + '...' : str;
}

function getMatchStrength(percentage) {
    if (percentage >= 80) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 40) return 'fair';
    return 'weak';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ==================== Initialization ==================== */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Resume Analyzer Chatbot loaded successfully!');
    console.log('API Base URL:', API_BASE_URL);
    
    // Initial state - with null checks
    // if (chatInput) chatInput.disabled = true;
    // if (sendBtn) sendBtn.disabled = true;
    // if (searchJobsBtn) searchJobsBtn.disabled = true;
    
    // Log all elements for debugging
    console.log('DOM Elements status:');
    console.log('- resumeFile:', resumeFile ? 'OK' : 'NOT FOUND');
    console.log('- uploadBtn:', uploadBtn ? 'OK' : 'NOT FOUND');
    console.log('- chatInput:', chatInput ? 'OK' : 'NOT FOUND');
    console.log('- sendBtn:', sendBtn ? 'OK' : 'NOT FOUND');
    console.log('- searchJobsBtn:', searchJobsBtn ? 'OK' : 'NOT FOUND');
    console.log('- chatContainer:', chatContainer ? 'OK' : 'NOT FOUND');
    console.log('- resumeInfo:', resumeInfo ? 'OK' : 'NOT FOUND');
});

/* ==================== Service Worker (Optional PWA support) ==================== */

if ('serviceWorker' in navigator) {
    // Service worker registration can be added here for PWA features
}
