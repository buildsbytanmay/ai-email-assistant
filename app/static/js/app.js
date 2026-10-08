
document.addEventListener('DOMContentLoaded', () => {
    // Analyze Form Handler
    const analyzeForm = document.getElementById('analyze-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const subject = document.getElementById('subject').value;
            const content = document.getElementById('content').value;
            const btn = document.getElementById('analyze-btn');
            const btnText = btn.querySelector('.btn-text');
            const loader = btn.querySelector('.loader');
            const errorMsg = document.getElementById('error-message');
            
            // Reset states
            errorMsg.classList.add('hidden');
            btn.disabled = true;
            btnText.style.opacity = '0';
            loader.classList.remove('hidden');
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ subject, content })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'An error occurred during analysis');
                }
                
                showResult(data);
                
            } catch (err) {
                errorMsg.textContent = err.message;
                errorMsg.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btnText.style.opacity = '1';
                loader.classList.add('hidden');
            }
        });
    }
    
    // Copy Reply Button
    const copyBtn = document.getElementById('copy-reply-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const reply = document.getElementById('res-reply').textContent;
            navigator.clipboard.writeText(reply).then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('btn-primary');
                copyBtn.classList.remove('btn-outline');
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.classList.remove('btn-primary');
                    copyBtn.classList.add('btn-outline');
                }, 2000);
            });
        });
    }
});

function showResult(data) {
    document.getElementById('empty-state').classList.add('hidden');
    const resultCard = document.getElementById('result-card');
    resultCard.classList.remove('hidden');
    
    // Set Badge
    const badge = document.getElementById('res-badge');
    badge.textContent = data.category;
    badge.className = 'badge badge-' + data.category.toLowerCase();
    
    // Set Confidence
    const confPct = Math.round(data.confidence * 100);
    setTimeout(() => {
        document.getElementById('res-confidence-bar').style.width = confPct + '%';
    }, 100);
    document.getElementById('res-confidence-text').textContent = confPct + '% confident';
    
    // Set Summary
    document.getElementById('res-summary').textContent = data.summary;
    
    // Set Reply
    document.getElementById('res-reply').textContent = data.generated_reply;
    
    // Demo Mode Notice
    const demoIndicator = document.getElementById('demo-indicator');
    if (data.is_demo) {
        demoIndicator.classList.remove('hidden');
    } else {
        demoIndicator.classList.add('hidden');
    }
}

async function loadHistory() {
    const tableBody = document.getElementById('history-body');
    const emptyState = document.getElementById('history-empty');
    const loader = document.getElementById('history-loader');
    
    if (!tableBody) return;
    
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        loader.classList.add('hidden');
        
        if (data.length === 0) {
            emptyState.classList.remove('hidden');
            return;
        }
        
        tableBody.innerHTML = '';
        data.forEach(item => {
            const date = new Date(item.created_at).toLocaleDateString();
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${date}</td>
                <td style="font-weight: 500;">${item.subject}</td>
                <td><span class="badge badge-${item.category.toLowerCase()}">${item.category}</span></td>
                <td class="col-summary"><div class="summary-truncate">${item.summary}</div></td>
                <td>
                    <button class="btn-danger-text" onclick="deleteHistory(${item.id}, this)">Delete</button>
                </td>
            `;
            tableBody.appendChild(tr);
        });
        
    } catch (err) {
        console.error("Failed to load history", err);
        loader.classList.add('hidden');
    }
}

async function deleteHistory(id, btnElement) {
    if (!confirm("Are you sure you want to delete this record?")) return;
    
    const tr = btnElement.closest('tr');
    tr.style.opacity = '0.5';
    
    try {
        const response = await fetch(`/api/history/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            tr.remove();
            
            const tableBody = document.getElementById('history-body');
            if (tableBody.children.length === 0) {
                document.getElementById('history-empty').classList.remove('hidden');
            }
        } else {
            throw new Error('Failed to delete');
        }
    } catch (err) {
        console.error(err);
        tr.style.opacity = '1';
        alert('Failed to delete history record.');
    }
}
