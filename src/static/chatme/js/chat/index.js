document.querySelector('#room-name-input').focus();
        document.querySelector('#room-name-input').onkeyup = function(e) {
            if (e.key === 'Enter') { document.querySelector('#room-name-submit').click(); }
        };
        document.querySelector('#room-name-submit').onclick = function(e) {
            var roomNameInput = document.querySelector('#room-name-input').value.trim();
            var roomName = roomNameInput.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
            if (roomName) { window.location.pathname = '/chat/room/' + encodeURIComponent(roomName) + '/';}
            else { alert('Please enter a valid room name (alphanumeric and hyphens).'); }
        };
