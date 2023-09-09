document.addEventListener('DOMContentLoaded', function () {
    const reconnect_button = document.getElementById('reconnect_button');
    reconnect_button.addEventListener('click', function () {
        chrome.runtime.sendMessage({ action: 'reconnect_websocket' });
    });
});