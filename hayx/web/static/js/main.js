document.addEventListener("DOMContentLoaded", function () {
    const socket = io();

    // Connection status
    socket.on('connect', function () {
        updateConnectionStatus(true);
    });

    socket.on('disconnect', function () {
        updateConnectionStatus(false);
    });

    // Receive live stats updates
    socket.on('stats_update', function (data) {
        updateStatsBar(data);
    });

    // Utility: Update status bar
    function updateStatsBar(data) {
        if (!data || !data.blockchain) return;

        const blockHeight = data.blockchain.total_blocks || 0;
        const walletBalance = data.mining?.wallet_balance || data.wallet?.balance || 0;

        const blockEl = document.getElementById("block-height");
        const balanceEl = document.getElementById("balance");

        if (blockEl) blockEl.textContent = `Block: ${blockHeight}`;
        if (balanceEl) balanceEl.textContent = `Balance: ${walletBalance.toFixed(8)} HayX`;
    }

    function updateConnectionStatus(connected) {
        const statusEl = document.getElementById("connection-status");
        if (statusEl) {
            statusEl.textContent = connected ? "🟢 Connected" : "🔴 Disconnected";
            statusEl.classList.toggle("connected", connected);
        }
    }

    // Theme toggle
    const themeBtn = document.getElementById("themeToggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const html = document.documentElement;
            const isDark = html.getAttribute("data-theme") === "dark";
            html.setAttribute("data-theme", isDark ? "light" : "dark");
            themeBtn.textContent = isDark ? "🌞" : "🌙";
        });
    }

    // Convert timestamp to human-readable format
    window.timestamp_to_date = function (ts) {
        const date = new Date(ts * 1000);
        return date.toLocaleString();
    };
});
