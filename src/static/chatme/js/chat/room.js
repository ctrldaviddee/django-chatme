const roomName = JSON.parse(document.getElementById('room-name').textContent);
        const currentUsername = JSON.parse(document.getElementById('user-username').textContent);
        const chatLog = document.getElementById('chat-log');
        const mainChatArea = document.getElementById('main-chat-area');
        const messageInputDom = document.getElementById('chat-message-input');
        const messageSubmitDom = document.getElementById('chat-message-submit');
        const onlineUsersListDom = document.getElementById('online-users-list');
        const onlineUsersCountDom = document.getElementById('online-users-count');

        function scrollToBottom() { mainChatArea.scrollTop = mainChatArea.scrollHeight; }
        scrollToBottom();

        const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const chatSocket = new WebSocket( wsProtocol + window.location.host + '/ws/chat/' + roomName + '/');

        chatSocket.onopen = function(e) { console.log('WebSocket connection established.'); };
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("Data received: ", data);
            if (data.type === 'chat_message') {
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
                messageElement.classList.add(data.username === currentUsername ? 'message-sent' : 'message-received');
                chatLog.appendChild(messageElement);
                scrollToBottom();
            } else if (data.type === 'presence_update') {
                onlineUsersListDom.innerHTML = '';
                data.users.sort().forEach(function(user) {
                    const userElement = document.createElement('li');
                    userElement.textContent = user;
                    if (user === currentUsername) userElement.classList.add('is-me');
                    onlineUsersListDom.appendChild(userElement);
                });
                onlineUsersCountDom.textContent = data.users.length;
                console.log("Presence update. Users:", data.users);
            }
        };
        chatSocket.onclose = function(e) {
            console.error('Chat socket closed. Code:', e.code, 'Reason:', e.reason, 'Was clean:', e.wasClean);
            const li = document.createElement('li'); li.style.color = 'red'; li.classList.add('message-received');
            li.textContent = 'Connection lost. Please refresh.'; chatLog.appendChild(li); scrollToBottom();
        };
        chatSocket.onerror = function(err) {
            console.error('WebSocket error:', err);
            const li = document.createElement('li'); li.style.color = 'red'; li.classList.add('message-received');
            li.textContent = 'WebSocket error. Please refresh.'; chatLog.appendChild(li); scrollToBottom();
        };
        messageInputDom.focus();
        messageInputDom.onkeyup = function(e) { if (e.key === 'Enter') messageSubmitDom.click(); };
        messageSubmitDom.onclick = function(e) {
            const message = messageInputDom.value;
            if (message.trim() === '') return;
            try {
                chatSocket.send(JSON.stringify({'type': 'chat_message', 'message': message}));
                messageInputDom.value = '';
            } catch (err) { console.error("Error sending message:", err); }
        };
