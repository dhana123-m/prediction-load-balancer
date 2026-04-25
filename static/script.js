let oldCpu = 0;
let oldRam = 0;
let oldDisk = 0;
let oldBattery = 0;

/* ===============================
   CHART
=============================== */
const ctx = document.getElementById("myChart");

let myChart = null;

if (ctx) {
    myChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "CPU %",
                    data: [],
                    borderWidth: 3,
                    tension: 0.4
                },
                {
                    label: "RAM %",
                    data: [],
                    borderWidth: 3,
                    tension: 0.4
                },
                {
                    label: "Disk %",
                    data: [],
                    borderWidth: 3,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

/* ===============================
   SOCKET.IO
=============================== */
if (typeof io !== "undefined") {
    const socket = io();

    socket.on("metrics_update", function (data) {
        updateDashboard(data);

        if (data.risk === "Critical") {
            showToast("⚠ Critical Risk Detected");
        }

        if (data.heavy_cpu > 90) {
            showToast("⚠ Heavy Application Overload");
        }
    });
}

/* ===============================
   ANIMATION
=============================== */
function animateBox(id, label, start, end) {

    const el = document.getElementById(id);
    if (!el) return;

    let current = start;
    let step = (end - start) / 30;

    let timer = setInterval(() => {

        current += step;

        if (
            (step > 0 && current >= end) ||
            (step < 0 && current <= end)
        ) {
            current = end;
            clearInterval(timer);
        }

        el.innerHTML = label + ": " + Math.round(current) + "%";

    }, 20);
}

/* ===============================
   TOAST
=============================== */
function showToast(msg) {

    const toast = document.getElementById("toast");
    if (!toast) return;

    toast.innerHTML = msg;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

/* ===============================
   UPDATE UI
=============================== */
function updateDashboard(data) {

    animateBox("cpu", "CPU", oldCpu, data.cpu);
    animateBox("ram", "RAM", oldRam, data.ram);
    animateBox("disk", "Disk", oldDisk, data.disk);
    animateBox("battery", "Battery", oldBattery, data.battery);

    oldCpu = data.cpu;
    oldRam = data.ram;
    oldDisk = data.disk;
    oldBattery = data.battery;

    setText("network", "Network: " + data.network + " MB");
    setText("prediction", "Prediction: " + data.prediction);
    setText("status", "Load Balancer: " + data.status);
    setText("risk", "Risk Level: " + data.risk);

    if (data.temp == 0) {
        setText("temp", "Temperature: Not Supported");
    } else {
        setText("temp", "Temperature: " + data.temp + "°C");
    }

    setText("warning", "Warning: " + data.warning_message);

    setText(
        "process",
        "Heavy App: " +
        data.heavy_name +
        " (" +
        data.heavy_cpu +
        "% CPU)"
    );

    /* Warning colors */
    const warn = document.getElementById("warning");
    if (warn) {
        warn.style.background =
            data.warning_message !== "No Warning"
                ? "orange"
                : "#333";
    }

    /* Heavy process colors */
    const box = document.getElementById("process");
    if (box) {
        if (data.heavy_cpu > 70) {
            box.style.background = "red";
        } else if (data.heavy_cpu > 40) {
            box.style.background = "orange";
        } else {
            box.style.background = "#333";
        }
    }

    /* Risk colors */
    const riskBox = document.getElementById("risk");
    if (riskBox) {
        if (data.risk === "Critical") {
            riskBox.style.background = "red";
        } else if (data.risk === "Warning") {
            riskBox.style.background = "orange";
        } else {
            riskBox.style.background = "green";
        }
    }

    updateChart(data);
}

/* ===============================
   CHART UPDATE
=============================== */
function updateChart(data) {

    if (!myChart) return;

    const time = new Date().toLocaleTimeString();

    myChart.data.labels.push(time);
    myChart.data.datasets[0].data.push(data.cpu);
    myChart.data.datasets[1].data.push(data.ram);
    myChart.data.datasets[2].data.push(data.disk);

    if (myChart.data.labels.length > 10) {
        myChart.data.labels.shift();

        myChart.data.datasets[0].data.shift();
        myChart.data.datasets[1].data.shift();
        myChart.data.datasets[2].data.shift();
    }

    myChart.update();
}

/* ===============================
   FETCH METRICS
=============================== */
function loadMetrics() {

    fetch("/metrics")
        .then(response => response.json())
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => {
            console.log("Metrics error:", error);
        });
}

/* ===============================
   HELPERS
=============================== */
function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = text;
}

/* ===============================
   PAGE LOAD
=============================== */
window.onload = function () {

    const loader = document.getElementById("loader");
    if (loader) {
        loader.style.display = "none";
    }

    const bar = document.getElementById("bar");
    if (bar) {
        setTimeout(() => {
            bar.style.width = "100%";
        }, 300);
    }

    loadMetrics();
    setInterval(loadMetrics, 3000);
};