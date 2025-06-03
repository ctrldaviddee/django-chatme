const roomName = JSON.parse(document.getElementById('room-name').textContent);
        const currentUsername = JSON.parse(document.getElementById('user-username').textContent);
        const chatLog = document.getElementById('chat-log');
        const chatLogContainer = document.getElementById('chat-log-container');
        const messageInputDom = document.getElementById('chat-message-input');
        const messageSubmitDom = document.getElementById('chat-message-submit');

        function scrollToBottom() {
            chatLogContainer.scrollTop = chatLogContainer.scrollHeight;
        }
        scrollToBottom(); // Scroll on initial load

        // Determine WebSocket protocol (ws or wss)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const chatSocket = new WebSocket(
            wsProtocol
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );

        chatSocket.onopen = function(e) {
            console.log('WebSocket connection established.');
            // You could fetch past messages here if not pre-loaded by Django template
        };

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("Data received: ", data);

            const messageElement = document.createElement('li');

            const metaDiv = document.createElement('div');
            metaDiv.classList.add('message-meta');

            const usernameSpan = document.createElement('span');
            usernameSpan.classList.add('message-username');
            usernameSpan.textContent = data.username;
            metaDiv.appendChild(usernameSpan);

            if (data.timestamp) {
                const timestampSpan = document.createElement('span');
                timestampSpan.classList.add('message-timestamp');
                const date = new Date(data.timestamp);
                timestampSpan.textContent = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                metaDiv.appendChild(timestampSpan);
            }

            messageElement.appendChild(metaDiv);
            messageElement.appendChild(document.createTextNode(data.message));

            if (data.username === currentUsername) {
                messageElement.classList.add('message-sent');
            } else {
                messageElement.classList.add('message-received');
            }

            chatLog.appendChild(messageElement);
            scrollToBottom(); // Scroll when new message arrives
        };

        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly. Code:', e.code, 'Reason:', e.reason);
            // Optionally, display a message to the user or attempt to reconnect
            const errorElement = document.createElement('li');
            errorElement.style.color = 'red';
            errorElement.textContent = 'Connection lost. Please refresh the page.';
            chatLog.appendChild(errorElement);
            scrollToBottom();
        };

        chatSocket.onerror = function(err) {
            console.error('WebSocket error:', err);
            const errorElement = document.createElement('li');
            errorElement.style.color = 'red';
            errorElement.textContent = 'WebSocket error. Please refresh the page.';
            chatLog.appendChild(errorElement);
            scrollToBottom();
        };

        messageInputDom.focus();
        messageInputDom.onkeyup = function(e) {
            if (e.key === 'Enter') {  // enter, return
                messageSubmitDom.click();
            }
        };

        messageSubmitDom.onclick = function(e) {
            const message = messageInputDom.value;
            if (message.trim() === '') {
                return; // Don't send empty messages
            }
            try {
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
                messageInputDom.value = ''; // Clear input field
            } catch (err) {
                console.error("Error sending message via WebSocket: ", err);
                // Handle cases where socket might not be open, etc.
            }
        };
