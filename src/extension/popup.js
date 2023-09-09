document.addEventListener('DOMContentLoaded', function () {
    const startButton = document.getElementById('startButton');

    startButton.addEventListener('click', function () {
        // 在這裡觸發資料收集操作
        chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
            const activeTab = tabs[0];
            chrome.tabs.sendMessage(activeTab.id, { action: 'startDataCollection' });
        });
    });
});