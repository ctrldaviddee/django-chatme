document.querySelector('#room-name-input').focus();
    document.querySelector('#room-name-input').onkeyup = function(e) {
        if (e.key === 'Enter') {  // enter, return
            document.querySelector('#room-name-submit').click();
        }
    };

    document.querySelector('#room-name-submit').onclick = function(e) {
        const roomName = document.querySelector('#room-name-input').value.trim();
        if (roomName) {
            window.location.pathname = '/chat/room/' + encodeURIComponent(roomName) + '/';
        } else {
            alert('Please enter a room name.');
        }
    };
