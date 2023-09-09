function kkbox_page_js() {
    chrome.tabs.query({}, function (tabs) {
        tabs.forEach(function (tab) {
            if (tab.url.includes('play.kkbox.com')) {
                chrome.scripting.executeScript({
                    target : {tabId : tab.id},
                    files : [ "content.js" ],
                });
                // console.log(play_status);
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
        // console.log(kkbox_data);
    }
});

function connectWebSocket() {
    socket = new WebSocket('ws://localhost:9239');

    socket.onopen = function () {
        console.log('WebSocket 連線已開啟');
    };

    socket.onmessage = function (event) {
        const message = event.data;
        console.log(`接收到訊息: ${message}`);
        // chrome.runtime.sendMessage({ action: 'websocketMessage', message });
    };

    socket.onclose = function () {
        // setTimeout(connectWebSocket, 1000);
        console.log('WebSocket 連線已關閉');
    };
}

function send_data_to_host(data) {
    socket.send(JSON.stringify(data));
}

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    if (message.action == 'reconnect_websocket') {
        socket.close();
        connectWebSocket();
    }
});

let socket = null;
connectWebSocket();

const intervalTime = 1000;
setInterval(kkbox_page_js, intervalTime);