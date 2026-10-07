function setUpDownload(content, filename = "teste.csv") {
    const link = document.createElement("a");
    
    // Check if it's a data URL (for PDFs, images, etc.)
    if (content.startsWith('data:')) {
        link.href = content;
    } else {
        // Treat as regular content, create a Blob (for CSV)
        const blob = new Blob(["\uFEFF" + content], {
            type: "text/csv;charset=utf-8;"
        });
        link.href = URL.createObjectURL(blob);
    }
    
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Only revoke if it was a created object URL (not a data URL)
    if (!content.startsWith('data:')) {
        URL.revokeObjectURL(link.href);
    }
}

async function sendMessage(message, bubble) {
    const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        
        // Remove previous tool card if a new tool card is being added
        if (chunk.includes('chat-tool-card')) {
            bubble.innerHTML = bubble.innerHTML.replace(/(<br\s*\/?>)+$/, ''); // Remove the trailing <br>s
            const oldCard = bubble.querySelector('.chat-tool-card:not(.chat-tool-complete)');
            if (oldCard) oldCard.remove();
        }
        
        // Convert newlines to <br> first
        let processed = chunk.replace(/\n/g, '<br>');
        
        // Sanitize with DOMPurify, allowing safe tags like <div>, <br>
        const config = {
            ALLOWED_TAGS: ['div', 'br', 'p', 'span', 'b', 'i', 'strong', 'em', 'img', 'a', 'button'],
            ALLOWED_ATTR: ['class', 'src', 'style', 'alt', 'href', 'download', 'data-pdf-url', 'data-filename']
        };
        const clean = DOMPurify.sanitize(processed, config);
        
        bubble.innerHTML += clean;
        
        // Attach click listeners to PDF download buttons
        const pdfButtons = bubble.querySelectorAll('.download-artifact-container');
        pdfButtons.forEach(btn => {
            if (!btn.hasListener) {
                btn.addEventListener('click', function() {
                    const url = this.getAttribute('data-pdf-url');
                    const filename = this.getAttribute('data-filename');
                    setUpDownload(url, filename);
                });
                btn.hasListener = true;
            }
        });
    }
}