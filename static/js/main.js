        // ── State ──
        let conversationHistory = [];
        let isWaitingForResponse = false;

        // ── DOM Elements ──
        const chatWindow = document.getElementById('chat-window');
        const msgInput = document.getElementById('msg-input');
        const sendBtn = document.getElementById('send-btn');
        const typingContainer = document.getElementById('typing-container');

        // ── Config ──
        marked.setOptions({ breaks: true, gfm: true });

        // ── Input Handling ──
        msgInput.addEventListener('input', function() {
            // Auto resize textarea
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            if (this.scrollHeight > 150) {
                this.style.overflowY = 'auto';
            } else {
                this.style.overflowY = 'hidden';
            }
            sendBtn.disabled = this.value.trim() === '' || isWaitingForResponse;
        });

        msgInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        sendBtn.addEventListener('click', handleSend);

        // ── Core Logic ──
        async function handleSend() {
            const text = msgInput.value.trim();
            if (!text || isWaitingForResponse) return;

            // 1. Render User Message
            renderMessage('user', text);
            
            // 2. Clear Input
            msgInput.value = '';
            msgInput.style.height = 'auto';
            sendBtn.disabled = true;

            // 3. Prepare for API Call
            isWaitingForResponse = true;
            showTyping(true);

            // 4. Call Backend API with SSE streaming
            try {
                await streamBackendResponse(text);
                // After streaming completes successfully, add to history manually
                addMessageToHistory('user', text);
            } catch (err) {
                console.error(err);
                showTyping(false);
                renderMessage('error', `Error connecting to API. ${err.message}`);
            } finally {
                isWaitingForResponse = false;
                sendBtn.disabled = msgInput.value.trim() === '';
                msgInput.focus();
            }
        }

        function addMessageToHistory(role, content) {
            conversationHistory.push({ role, content });
        }

        // ── UI Rendering ──
        function renderMessage(role, content, isMarkdown = false) {
            const wrapper = document.createElement('div');
            wrapper.className = `message-wrapper ${role === 'user' ? 'user' : 'bot'}`;
            
            if (role !== 'error') {
                const sender = document.createElement('div');
                sender.className = 'message-sender';
                sender.textContent = role === 'user' ? 'You' : 'DeepAI';
                wrapper.appendChild(sender);
            }

            const bubble = document.createElement('div');
            bubble.className = `message-bubble ${role === 'error' ? 'error' : ''}`;
            
            if (isMarkdown) {
                bubble.innerHTML = marked.parse(content);
            } else if (role === 'error') {
                bubble.textContent = content; // raw text for errors
            } else {
                bubble.textContent = content;
            }

            wrapper.appendChild(bubble);
            chatWindow.insertBefore(wrapper, typingContainer);
            scrollToBottom();
            return bubble; // returning bubble for streaming updates
        }

        function showTyping(show) {
            if (show) {
                typingContainer.style.display = 'flex';
                typingContainer.querySelector('.typing-indicator').style.display = 'flex';
                scrollToBottom();
            } else {
                typingContainer.style.display = 'none';
            }
        }

        function scrollToBottom() {
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }

        // ── API Integration (Backend SSE Streaming) ──
        async function streamBackendResponse(userMessage) {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                // Send the exact new message + past history to server
                body: JSON.stringify({
                    message: userMessage,
                    history: conversationHistory
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error?.message || `HTTP ${response.status}`);
            }

            // Create empty placeholder bubble for streaming
            showTyping(false); // remove indicator as we start receiving tokens
            const wrapper = document.createElement('div');
            wrapper.className = 'message-wrapper bot';
            
            const sender = document.createElement('div');
            sender.className = 'message-sender';
            sender.textContent = 'DeepAI';
            wrapper.appendChild(sender);

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            wrapper.appendChild(bubble);
            chatWindow.insertBefore(wrapper, typingContainer);

            let streamedContent = '';
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            // Read the SSE stream
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.trim() === '' || !line.startsWith('data: ')) continue;
                    
                    const dataObjStr = line.slice(6);
                    if (dataObjStr.trim() === '[DONE]') break; // stream end sent by backend

                    try {
                        const data = JSON.parse(dataObjStr);
                        
                        // Handle potential API errors forwarded from backend
                        if (data.error) {
                            throw new Error(data.error.message);
                        }

                        // Typical token extraction handling structure from OpenAI/Groq standard
                        const token = data.choices[0]?.delta?.content;
                        if (token) {
                            streamedContent += token;
                            bubble.innerHTML = marked.parse(streamedContent); // re-parse markdown as it comes
                            scrollToBottom();
                        }
                    } catch (e) {
                        console.warn("Failed to parse stream JSON:", line, e);
                    }
                }
            }

            // After fully complete, save assistant message to history
            addMessageToHistory('assistant', streamedContent);
        }
