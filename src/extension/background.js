function kkbox_page_js() {
    chrome.tabs.query({}, function (tabs) {
        tabs.forEach(function (tab) {
            if (tab.url.includes('play.kkbox.com')) {
                chrome.scripting.executeScript({
                    target : {tabId : tab.id},
                    files : [ "content.js" ],
                });
            }
        });
    });
}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.type == "kkbox_data") {
        var kkbox_data = JSON.parse(request.options.kkbox_data);
        var send_data = {
            type: "kkbox_data",
            data: kkbox_data
        };
        send_data_to_host(send_data);
    }
});

function connectWebSocket() {
    socket = new WebSocket('ws://127.0.0.1:9239');

    socket.onerror = function () {
        console.log('WebSocket 連線錯誤');
    };

    socket.onopen = function () {
        console.log('WebSocket 連線已開啟');
    };

    socket.onmessage = function (event) {
        const message = event.data;
    };

    socket.onclose = function () {
    };
}

function isOpen(ws) {
    if (!ws) return false;
    return ws.readyState === ws.OPEN
}

function send_data_to_host(data) {
    if (!isOpen(socket)) return;
    socket.send(JSON.stringify(data));
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action == 'reconnect_websocket') {
        if (!isOpen(socket)) {
            connectWebSocket();
        }
    }
});

let socket = null;
const intervalTime = 1000;
setInterval(kkbox_page_js, intervalTime);